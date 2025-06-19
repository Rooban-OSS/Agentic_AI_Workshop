from app.database import jobs_collection, interviewers_collection, candidates_collection, panels_collection
from bson import ObjectId
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def create_job(job_data: Dict[str, Any]) -> str:
    try:
        job_data['created_at'] = datetime.now()
        job_data['status'] = 'active'
        result = jobs_collection.insert_one(job_data)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        raise

def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    try:
        return jobs_collection.find_one({"_id": ObjectId(job_id)})
    except Exception as e:
        logger.error(f"Error fetching job {job_id}: {e}")
        return None

def get_all_jobs(skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
    try:
        jobs = list(jobs_collection.find().skip(skip).limit(limit))
        for job in jobs:
            job['_id'] = str(job['_id'])
        return jobs
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        return []

def create_interviewer(interviewer_data: Dict[str, Any]) -> str:
    try:
        interviewer_data['created_at'] = datetime.now()
        interviewer_data['status'] = 'active'
        result = interviewers_collection.insert_one(interviewer_data)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error creating interviewer: {e}")
        raise

def get_interviewer(interviewer_id: str) -> Optional[Dict[str, Any]]:
    try:
        return interviewers_collection.find_one({"_id": ObjectId(interviewer_id)})
    except Exception as e:
        logger.error(f"Error fetching interviewer {interviewer_id}: {e}")
        return None

def get_filtered_interviewers(
    department: str = None,
    interviewer_type: str = None,
    skip: int = 0,
    limit: int = 20
) -> List[Dict[str, Any]]:
    try:
        filter_query = {"status": {"$ne": "deleted"}}
        if department:
            filter_query["department"] = department
        if interviewer_type:
            filter_query["interviewer_type"] = interviewer_type
        
        interviewers = list(
            interviewers_collection.find(filter_query)
            .skip(skip)
            .limit(limit)
        )
        for interviewer in interviewers:
            interviewer['_id'] = str(interviewer['_id'])
        return interviewers
    except Exception as e:
        logger.error(f"Error filtering interviewers: {e}")
        return []

def create_candidate(candidate_data: Dict[str, Any]) -> str:
    try:
        candidate_data['created_at'] = datetime.now()
        candidate_data['status'] = 'active'
        result = candidates_collection.insert_one(candidate_data)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error creating candidate: {e}")
        raise

def get_candidate(candidate_id: str) -> Optional[Dict[str, Any]]:
    try:
        return candidates_collection.find_one({"_id": ObjectId(candidate_id)})
    except Exception as e:
        logger.error(f"Error fetching candidate {candidate_id}: {e}")
        return None

def get_filtered_candidates(
    job_role: str = None,
    skip: int = 0,
    limit: int = 20
) -> List[Dict[str, Any]]:
    try:
        filter_query = {"status": {"$ne": "deleted"}}
        if job_role:
            filter_query["job_role"] = {"$regex": job_role, "$options": "i"}
        
        candidates = list(
            candidates_collection.find(filter_query)
            .skip(skip)
            .limit(limit)
        )
        for candidate in candidates:
            candidate['_id'] = str(candidate['_id'])
        return candidates
    except Exception as e:
        logger.error(f"Error filtering candidates: {e}")
        return []

def create_panel(panel_data: Dict[str, Any]) -> str:
    try:
        panel_data['created_at'] = datetime.now()
        panel_data['status'] = 'scheduled'
        result = panels_collection.insert_one(panel_data)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error creating panel: {e}")
        raise

def check_database_connection() -> bool:
    try:
        jobs_collection.find_one({})
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False

def get_interviewer_relationships(interviewer_ids: List[str]) -> List[Dict[str, Any]]:
    try:
        return list(interviewers_collection.find(
            {"_id": {"$in": [ObjectId(id) for id in interviewer_ids]}},
            {"past_collaborations": 1, "reporting_structure": 1, "department": 1, "_id": 1, "gender": 1, "ethnicity": 1}
        ))
    except Exception as e:
        logger.error(f"Error fetching interviewer relationships: {e}")
        return []