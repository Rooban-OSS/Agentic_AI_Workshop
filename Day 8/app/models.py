from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ExperienceLevel(str, Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"

class InterviewerType(str, Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    DOMAIN_EXPERT = "domain_expert"
    HR = "hr"
    MANAGER = "manager"

class ConflictStatus(str, Enum):
    NONE = "none"
    POTENTIAL = "potential"
    CONFIRMED = "confirmed"

class DEIComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"

class Job(BaseModel):
    job_role: str
    job_description: str
    required_skills: List[str]
    experience_level: ExperienceLevel
    department: str
    interviewer_types_needed: List[InterviewerType] = Field(
        default=[InterviewerType.TECHNICAL, InterviewerType.BEHAVIORAL]
    )

class Interviewer(BaseModel):
    name: str
    email: EmailStr
    department: str
    skills: List[str]
    availability: List[Dict[str, Any]]
    past_feedback_score: float = Field(ge=0.0, le=5.0)
    experience_level: ExperienceLevel
    interviewer_type: InterviewerType
    years_of_experience: int = Field(ge=0)
    gender: str
    ethnicity: str
    past_collaborations: List[str] = Field(default_factory=list)
    reporting_structure: Optional[str] = None

class Candidate(BaseModel):
    name: str
    email: EmailStr
    job_role: str
    skills: List[str]
    experience_level: ExperienceLevel

class PanelMember(BaseModel):
    interviewer_id: str
    name: str
    match_score: float
    role_in_panel: InterviewerType
    recommendation_reason: str
    conflict_status: ConflictStatus = ConflictStatus.NONE
    conflict_details: Optional[str] = None
    dei_compliance_status: DEIComplianceStatus = DEIComplianceStatus.COMPLIANT
    dei_issues: Optional[str] = None

class PanelRecommendation(BaseModel):
    recommended_panel: List[PanelMember]
    skill_coverage: Dict[str, Any]
    quality_metrics: Dict[str, Any]
    alternatives: List[Dict[str, Any]]
    conflict_summary: Dict[str, Any] = Field(default_factory=dict)
    dei_summary: Dict[str, Any] = Field(default_factory=dict)