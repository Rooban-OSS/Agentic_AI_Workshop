from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from app.database import interviewers_collection, jobs_collection, candidates_collection, vector_store
from app.models import InterviewerType, ExperienceLevel, PanelMember, PanelRecommendation, ConflictStatus, DEIComplianceStatus
from bson import ObjectId
import json
import logging
from typing import List, Dict, Any
from app.crud import get_interviewer_relationships
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.getenv("GEMINI_API_KEY"))

def initialize_vector_store():
    global vector_store
    if vector_store is None:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        best_practices = [
            Document(
                page_content="Optimal panel size is 3-5 members, balancing technical, behavioral, and managerial perspectives.",
                metadata={"source": "industry_best_practices"}
            ),
            Document(
                page_content="Include at least one technical interviewer for roles requiring specific skills like Python or Java.",
                metadata={"source": "industry_best_practices"}
            ),
            Document(
                page_content="Ensure panel includes diverse experience levels to cover both strategic and practical evaluation.",
                metadata={"source": "industry_best_practices"}
            ),
            Document(
                page_content="Behavioral interviewers should focus on cultural fit and soft skills for better team integration.",
                metadata={"source": "industry_best_practices"}
            ),
            Document(
                page_content="DEI policies require at least 30% representation of underrepresented genders and ethnicities in panels.",
                metadata={"source": "dei_policies"}
            ),
            Document(
                page_content="Panels should avoid over-representation of any single department to ensure diverse perspectives.",
                metadata={"source": "dei_policies"}
            )
        ]
        vector_store = FAISS.from_documents(best_practices, embeddings)

initialize_vector_store()

class SkillMatchAgent:
    def __init__(self):
        self.prompt = PromptTemplate(
            input_variables=["required_skills", "interviewer_skills", "job_description"],
            template="""
            Analyze the skill match between required skills and interviewer skills for this job:
            
            Job Description: {job_description}
            Required Skills: {required_skills}
            Interviewer Skills: {interviewer_skills}
            
            Return a JSON with:
            {{
                "semantic_match_score": float (0.0 to 1.0),
                "matching_skills": [list of matching skills],
                "skill_gaps": [list of missing skills]
            }}
            """
        )
        self.chain = LLMChain(llm=llm, prompt=self.prompt)

    def calculate_skill_match(self, required_skills: List[str], interviewer_skills: List[str], job_description: str = "") -> Dict[str, Any]:
        try:
            exact_matches = len(set(required_skills).intersection(set(interviewer_skills)))
            exact_score = exact_matches / len(required_skills) if required_skills else 0.0
            
            result = self.chain.run(
                required_skills=", ".join(required_skills),
                interviewer_skills=", ".join(interviewer_skills),
                job_description=job_description
            )
            semantic_data = json.loads(result.strip())
            semantic_score = semantic_data.get("semantic_match_score", 0.0)
            final_score = (exact_score * 0.4) + (semantic_score * 0.6)
            return {
                "match_score": min(final_score, 1.0),
                "matching_skills": semantic_data.get("matching_skills", []),
                "skill_gaps": semantic_data.get("skill_gaps", [])
            }
        except Exception as e:
            logger.error(f"Error in skill matching: {e}")
            return {"match_score": exact_score, "matching_skills": [], "skill_gaps": required_skills}

    def score_interviewers(self, job: Dict, interviewers: List[Dict]) -> List[Dict]:
        scored = []
        for interviewer in interviewers:
            skill_result = self.calculate_skill_match(
                job.get('required_skills', []),
                interviewer.get('skills', []),
                job.get('job_description', '')
            )
            quality_score = self._calculate_quality_score(interviewer)
            overall_score = (skill_result["match_score"] * 0.5) + (quality_score * 0.5)
            scored.append({
                "interviewer": interviewer,
                "skill_score": skill_result["match_score"],
                "quality_score": quality_score,
                "overall_score": overall_score,
                "matching_skills": skill_result["matching_skills"],
                "skill_gaps": skill_result["skill_gaps"]
            })
        return sorted(scored, key=lambda x: x["overall_score"], reverse=True)

    def _calculate_quality_score(self, interviewer: Dict) -> float:
        feedback_score = interviewer.get('past_feedback_score', 0.0) / 5.0
        years_exp = interviewer.get('years_of_experience', 0)
        exp_factor = min(years_exp / 10, 1.0)
        return (feedback_score * 0.6) + (exp_factor * 0.4)

class DEIComplianceAgent:
    def __init__(self):
        self.prompt = PromptTemplate(
            input_variables=["panel_composition", "dei_policies"],
            template="""
            Analyze the interview panel for DEI compliance based on the following composition and policies:

            Panel Composition: {panel_composition}
            DEI Policies: {dei_policies}

            Return a JSON with:
            {{
                "compliance_score": float (0.0 to 1.0),
                "compliance_status": ["compliant", "non_compliant"],
                "issues_detected": [list of issues],
                "panel_compliance": {{
                    "interviewer_id": {{
                        "status": ["compliant", "non_compliant"],
                        "issues": str or null
                    }}
                }}
            }}
            """
        )
        self.chain = LLMChain(llm=llm, prompt=self.prompt)

    def check_compliance(self, selected_interviewers: List[Dict], job: Dict = None) -> Dict[str, Any]:
        try:
            interviewer_ids = [str(interviewer["interviewer"]["_id"]) for interviewer in selected_interviewers]
            relationships = get_interviewer_relationships(interviewer_ids)
            
            panel_composition = {
                "interviewers": [
                    {
                        "id": str(interviewer["interviewer"]["_id"]),
                        "gender": rel.get("gender", "unknown"),
                        "ethnicity": rel.get("ethnicity", "unknown"),
                        "department": rel.get("department", "unknown"),
                        "experience_level": interviewer["interviewer"].get("experience_level", "unknown")
                    }
                    for interviewer, rel in zip(selected_interviewers, relationships)
                ],
                "job_department": job.get("department", "unknown") if job else "unknown"
            }
            
            query = f"DEI policies for panel composition: {json.dumps(panel_composition)}"
            relevant_docs = vector_store.similarity_search(query, k=2)
            dei_policies = "\n".join([doc.page_content for doc in relevant_docs])
            
            result = self.chain.run(
                panel_composition=json.dumps(panel_composition),
                dei_policies=dei_policies
            )
            compliance_data = json.loads(result.strip())
            
            compliance_score = compliance_data.get("compliance_score", 0.0)
            overall_status = compliance_data.get("compliance_status", "non_compliant")
            issues_detected = compliance_data.get("issues_detected", [])
            
            panel_compliance = {}
            for interviewer in selected_interviewers:
                interviewer_id = str(interviewer["interviewer"]["_id"])
                panel_compliance[interviewer_id] = compliance_data["panel_compliance"].get(interviewer_id, {
                    "status": "compliant",
                    "issues": None
                })
            
            return {
                "compliance_score": compliance_score,
                "overall_compliance_status": overall_status,
                "issues_detected": issues_detected,
                "panel_compliance": panel_compliance
            }
        except Exception as e:
            logger.error(f"Error in DEI compliance check: {e}")
            return {
                "compliance_score": 0.0,
                "overall_compliance_status": "non_compliant",
                "issues_detected": [str(e)],
                "panel_compliance": {
                    str(interviewer["interviewer"]["_id"]): {"status": "compliant", "issues": None}
                    for interviewer in selected_interviewers
                }
            }

class ConflictCheckerAgent:
    def __init__(self):
        self.prompt = PromptTemplate(
            input_variables=["panel_composition", "relationships"],
            template="""
            Check for conflicts of interest in the interview panel based on the following composition and relationships:

            Panel Composition: {panel_composition}
            Relationships: {relationships}

            Return a JSON with:
            {{
                "overall_conflict_level": ["none", "potential", "confirmed"],
                "conflicts_detected": [list of conflicts],
                "panel_conflicts": {{
                    "interviewer_id": {{
                        "status": ["none", "potential", "confirmed"],
                        "details": str or null
                    }}
                }}
            }}
            """
        )
        self.chain = LLMChain(llm=llm, prompt=self.prompt)

    def check_conflicts(self, selected_interviewers: List[Dict], candidate: Dict = None) -> Dict[str, Any]:
        try:
            interviewer_ids = [str(interviewer["interviewer"]["_id"]) for interviewer in selected_interviewers]
            relationships = get_interviewer_relationships(interviewer_ids)
            
            panel_composition = {
                "interviewers": [
                    {
                        "id": str(interviewer["interviewer"]["_id"]),
                        "name": interviewer["interviewer"]["name"],
                        "department": interviewer["interviewer"].get("department", "unknown")
                    }
                    for interviewer in selected_interviewers
                ],
                "candidate_department": candidate.get("department", "unknown") if candidate else "unknown"
            }
            
            result = self.chain.run(
                panel_composition=json.dumps(panel_composition),
                relationships=json.dumps(relationships)
            )
            conflict_data = json.loads(result.strip())
            
            return conflict_data
        except Exception as e:
            logger.error(f"Error checking conflicts: {e}")
            return {
                "overall_conflict_level": "none",
                "conflicts_detected": [],
                "panel_conflicts": {
                    str(interviewer["interviewer"]["_id"]): {"status": "none", "details": None}
                    for interviewer in selected_interviewers
                }
            }

class PanelDesignOptimizerAgent:
    def __init__(self):
        self.prompt = PromptTemplate(
            input_variables=["job_info", "candidate_info", "context"],
            template="""
            Recommend the ideal panel composition based on industry best practices:

            Best Practices Context: {context}
            Job Information: {job_info}
            Candidate Information: {candidate_info}

            Provide recommendations for:
            1. Panel size
            2. Required interviewer types and their roles
            3. Experience level mix
            4. Specific skills needed

            Return a JSON response with:
            {{
                "recommended_panel_size": int,
                "interviewer_types_needed": [
                    {{
                        "type": "technical|behavioral|domain_expert|hr|manager",
                        "count": int,
                        "primary_focus": "description",
                        "required_skills": [list]
                    }}
                ],
                "experience_level_mix": {{
                    "senior": int,
                    "mid": int,
                    "junior": int
                }},
                "special_considerations": [list]
            }}
            """
        )
        self.chain = LLMChain(llm=llm, prompt=self.prompt)

    def generate_strategy(self, job: Dict, candidate: Dict = None) -> Dict[str, Any]:
        job_info = f"Role: {job.get('job_role', 'N/A')}, Department: {job.get('department', 'N/A')}, Required Skills: {', '.join(job.get('required_skills', []))}"
        candidate_info = f"Experience Level: {candidate.get('experience_level', 'N/A')}, Skills: {', '.join(candidate.get('skills', []))}" if candidate else "Not provided"
        
        query = f"Optimal panel composition for job: {job_info}, candidate: {candidate_info}"
        try:
            relevant_docs = vector_store.similarity_search(query, k=3)
            context = "\n".join([doc.page_content for doc in relevant_docs])
        except Exception as e:
            logger.error(f"Error in RAG retrieval: {e}")
            context = "Default best practices: 3-5 member panel with technical and behavioral interviewers."
        
        try:
            result = self.chain.run(job_info=job_info, candidate_info=candidate_info, context=context)
            return json.loads(result.strip())
        except Exception as e:
            logger.error(f"Error generating panel strategy: {e}")
            return {
                "recommended_panel_size": 3,
                "interviewer_types_needed": [
                    {"type": "technical", "count": 1, "primary_focus": "Technical skills assessment", "required_skills": job.get('required_skills', [])},
                    {"type": "behavioral", "count": 1, "primary_focus": "Soft skills and cultural fit", "required_skills": []}
                ],
                "experience_level_mix": {"senior": 1, "mid": 1, "junior": 0},
                "special_considerations": []
            }

    def select_panel(self, panel_strategy: Dict, scored_interviewers: List[Dict]) -> List[Dict]:
        panel_size = panel_strategy.get("recommended_panel_size", 3)
        selected_panel = []
        by_type = {}
        for item in scored_interviewers:
            interviewer_type = item["interviewer"].get("interviewer_type", InterviewerType.TECHNICAL)
            if interviewer_type not in by_type:
                by_type[interviewer_type] = []
            by_type[interviewer_type].append(item)
        
        for type_req in panel_strategy.get("interviewer_types_needed", []):
            type_name = type_req["type"]
            count_needed = type_req["count"]
            if type_name in by_type:
                candidates = sorted(by_type[type_name], key=lambda x: x["overall_score"], reverse=True)
                selected_panel.extend(candidates[:count_needed])
        
        remaining_slots = panel_size - len(selected_panel)
        if remaining_slots > 0:
            selected_ids = {item["interviewer"]["_id"] for item in selected_panel}
            remaining_candidates = [
                item for item in scored_interviewers 
                if item["interviewer"]["_id"] not in selected_ids
            ]
            remaining_candidates.sort(key=lambda x: x["overall_score"], reverse=True)
            selected_panel.extend(remaining_candidates[:remaining_slots])
        
        return selected_panel[:panel_size]

class AgentOrchestrator:
    def __init__(self):
        self.skill_match_agent = SkillMatchAgent()
        self.dei_compliance_agent = DEIComplianceAgent()
        self.conflict_checker_agent = ConflictCheckerAgent()
        self.panel_design_agent = PanelDesignOptimizerAgent()

    def generate_recommendation(self, entity_id: str, is_final: bool = False) -> PanelRecommendation:
        try:
            if is_final:
                candidate = candidates_collection.find_one({"_id": ObjectId(entity_id)})
                if not candidate:
                    raise ValueError("Candidate not found")
                job = jobs_collection.find_one({"job_role": candidate["job_role"]})
                if not job:
                    raise ValueError("Job not found")
            else:
                job = jobs_collection.find_one({"_id": ObjectId(entity_id)})
                if not job:
                    raise ValueError("Job not found")
                candidate = None
            
            all_interviewers = list(interviewers_collection.find())
            
            panel_strategy = self.panel_design_agent.generate_strategy(job, candidate)
            
            scored_interviewers = self.skill_match_agent.score_interviewers(job, all_interviewers)
            
            selected_panel = self.panel_design_agent.select_panel(panel_strategy, scored_interviewers)
            
            conflict_info = self.conflict_checker_agent.check_conflicts(selected_panel, candidate)
            
            dei_info = self.dei_compliance_agent.check_compliance(selected_panel, job)
            
            panel_members = [
                PanelMember(
                    interviewer_id=str(item["interviewer"]["_id"]),
                    name=item["interviewer"]["name"],
                    match_score=item["skill_score"],
                    role_in_panel=item["interviewer"].get("interviewer_type", InterviewerType.TECHNICAL),
                    recommendation_reason=f"Skill match score: {item['skill_score']:.2f}, Quality score: {item['quality_score']:.2f}",
                    conflict_status=conflict_info["panel_conflicts"][str(item["interviewer"]["_id"])]["status"],
                    conflict_details=conflict_info["panel_conflicts"][str(item["interviewer"]["_id"])]["details"],
                    dei_compliance_status=dei_info["panel_compliance"][str(item["interviewer"]["_id"])]["status"],
                    dei_issues=dei_info["panel_compliance"][str(item["interviewer"]["_id"])]["issues"]
                )
                for item in selected_panel
            ]
            
            panel_skills = set()
            for item in selected_panel:
                panel_skills.update(item["interviewer"].get("skills", []))
            covered_skills = list(set(job.get('required_skills', [])).intersection(panel_skills))
            missing_skills = list(set(job.get('required_skills', [])).difference(panel_skills))
            coverage_score = len(covered_skills) / len(job.get('required_skills', [])) if job.get('required_skills', []) else 1.0
            
            avg_overall_score = sum(item["overall_score"] for item in selected_panel) / len(selected_panel) if selected_panel else 0.0
            quality_metrics = {
                "overall_quality": round(avg_overall_score, 3),
                "panel_size": len(selected_panel),
                "quality_rating": "excellent" if avg_overall_score >= 0.8 else "good" if avg_overall_score >= 0.6 else "fair"
            }
            
            selected_ids = {item["interviewer"]["_id"] for item in selected_panel}
            alternatives = [
                {
                    "interviewer_id": str(item["interviewer"]["_id"]),
                    "name": item["interviewer"]["name"],
                    "overall_score": item["overall_score"],
                    "reason": f"Alternative with score {item['overall_score']:.2f}"
                }
                for item in scored_interviewers if item["interviewer"]["_id"] not in selected_ids and item["overall_score"] >= 0.4
            ][:3]
            
            return PanelRecommendation(
                recommended_panel=panel_members,
                skill_coverage={
                    "coverage_score": coverage_score,
                    "covered_skills": covered_skills,
                    "missing_skills": missing_skills
                },
                quality_metrics=quality_metrics,
                alternatives=alternatives,
                conflict_summary={
                    "overall_conflict_level": conflict_info["overall_conflict_level"],
                    "conflicts_detected": conflict_info["conflicts_detected"]
                },
                dei_summary={
                    "compliance_score": dei_info["compliance_score"],
                    "issues_detected": dei_info["issues_detected"]
                }
            )
        
        except Exception as e:
            logger.error(f"Error in recommendation: {e}")
            raise
