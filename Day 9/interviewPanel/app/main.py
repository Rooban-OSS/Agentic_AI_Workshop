from fastapi import FastAPI, HTTPException, Query
from app.models import Job, Interviewer, Candidate, PanelRecommendation
import app.crud
from app.agents import AgentOrchestrator
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Interview Panel Optimizer API",
    description="AI-powered interview panel optimization with Skill Match, DEI Compliance, Conflict Checker, and Panel Design Optimizer agents",
    version="2.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "Interview Panel Optimizer API",
        "version": "2.2.0",
        "features": [
            "Skill Match Agent",
            "DEI Compliance Agent",
            "Conflict Checker Agent",
            "Panel Design Optimizer Agent with RAG"
        ]
    }

@app.post("/job/create")
def create_job(job: Job):
    try:
        job_id = crud.create_job(job.dict())
        logger.info(f"Job created successfully: {job_id}")
        return {
            "message": "Job created successfully",
            "job_id": job_id,
            "job_role": job.job_role,
            "department": job.department
        }
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")

@app.get("/job/{job_id}")
def get_job(job_id: str):
    try:
        job = crud.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        job['_id'] = str(job['_id'])
        return job
    except Exception as e:
        logger.error(f"Error fetching job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch job: {str(e)}")

@app.get("/jobs")
def list_jobs(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
    try:
        jobs = crud.get_all_jobs(skip=skip, limit=limit)
        return {
            "jobs": jobs,
            "count": len(jobs),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")

@app.post("/interviewer/add")
def add_interviewer(interviewer: Interviewer):
    try:
        interviewer_id = crud.create_interviewer(interviewer.dict())
        logger.info(f"Interviewer added successfully: {interviewer_id}")
        return {
            "message": "Interviewer added successfully",
            "interviewer_id": interviewer_id,
            "name": interviewer.name,
            "department": interviewer.department
        }
    except Exception as e:
        logger.error(f"Error adding interviewer: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add interviewer: {str(e)}")

@app.get("/interviewers")
def list_interviewers(
    department: Optional[str] = None,
    interviewer_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    try:
        interviewers = crud.get_filtered_interviewers(
            department=department,
            interviewer_type=interviewer_type,
            skip=skip,
            limit=limit
        )
        return {
            "interviewers": interviewers,
            "count": len(interviewers),
            "filters": {
                "department": department,
                "interviewer_type": interviewer_type
            }
        }
    except Exception as e:
        logger.error(f"Error listing interviewers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list interviewers: {str(e)}")

@app.post("/candidate/register")
def register_candidate(candidate: Candidate):
    try:
        candidate_id = crud.create_candidate(candidate.dict())
        logger.info(f"Candidate registered successfully: {candidate_id}")
        return {
            "message": "Candidate registered successfully",
            "candidate_id": candidate_id,
            "name": candidate.name,
            "job_role": candidate.job_role
        }
    except Exception as e:
        logger.error(f"Error registering candidate: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to register candidate: {str(e)}")

@app.get("/candidates")
def list_candidates(
    job_role: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    try:
        candidates = crud.get_filtered_candidates(
            job_role=job_role,
            skip=skip,
            limit=limit
        )
        return {
            "candidates": candidates,
            "count": len(candidates),
            "filters": {
                "job_role": job_role
            }
        }
    except Exception as e:
        logger.error(f"Error listing candidates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list candidates: {str(e)}")

@app.get("/job/{job_id}/recommend_panel")
def recommend_panel(job_id: str):
    try:
        orchestrator = AgentOrchestrator()
        recommendation = orchestrator.generate_recommendation(job_id, is_final=False)
        return {
            "job_id": job_id,
            "recommendation_type": "initial",
            "recommended_panel": [
                {
                    "interviewer_id": member.interviewer_id,
                    "name": member.name,
                    "match_score": member.match_score,
                    "role_in_panel": member.role_in_panel,
                    "recommendation_reason": member.recommendation_reason,
                    "conflict_status": member.conflict_status,
                    "dei_compliance_status": member.dei_compliance_status,
                    "dei_issues": member.dei_issues
                }
                for member in recommendation.recommended_panel
            ],
            "skill_coverage": recommendation.skill_coverage,
            "quality_metrics": recommendation.quality_metrics,
            "alternatives": recommendation.alternatives,
            "conflict_summary": recommendation.conflict_summary,
            "dei_summary": recommendation.dei_summary
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error recommending panel for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@app.get("/candidate/{candidate_id}/suggest_panel")
def suggest_panel(candidate_id: str):
    try:
        orchestrator = AgentOrchestrator()
        recommendation = orchestrator.generate_recommendation(candidate_id, is_final=True)
        return {
            "candidate_id": candidate_id,
            "recommendation_type": "final",
            "recommended_panel": [
                {
                    "interviewer_id": member.interviewer_id,
                    "name": member.name,
                    "match_score": member.match_score,
                    "role_in_panel": member.role_in_panel,
                    "recommendation_reason": member.recommendation_reason,
                    "conflict_status": member.conflict_status,
                    "dei_compliance_status": member.dei_compliance_status,
                    "dei_issues": member.dei_issues
                }
                for member in recommendation.recommended_panel
            ],
            "skill_coverage": recommendation.skill_coverage,
            "quality_metrics": recommendation.quality_metrics,
            "alternatives": recommendation.alternatives,
            "conflict_summary": recommendation.conflict_summary,
            "dei_summary": recommendation.dei_summary
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error suggesting panel for candidate {candidate_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate panel: {str(e)}")

@app.get("/health")
def health_check():
    try:
        db_status = crud.check_database_connection()
        return {
            "status": "healthy" if db_status else "unhealthy",
            "database": "connected" if db_status else "disconnected",
            "version": "2.2.0",
            "features_active": [
                "skill_matching",
                "dei_compliance",
                "conflict_checking",
                "panel_design_optimization"
            ]
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "version": "2.2.0"
        }