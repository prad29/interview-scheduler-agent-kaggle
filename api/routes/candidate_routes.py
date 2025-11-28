from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from typing import List, Optional
from pydantic import BaseModel, EmailStr
import os
import shutil
from datetime import datetime
import asyncio

from agents.orchestrator_agent import OrchestratorAgent
from tools.pdf_parser import extract_text_from_pdf
from tools.docx_parser import extract_text_from_docx
from storage.file_storage import FileStorage
from config import config
from api.middleware.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# File storage
file_storage = FileStorage(config.RESUME_STORAGE_PATH)

# Initialize orchestrator
orchestrator = OrchestratorAgent()

# Pydantic models
class CandidateResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    overall_score: float
    skills_match_score: float
    cultural_fit_score: float
    tier: str
    matched_skills: List[str]
    missing_skills: List[str]

class BatchProcessRequest(BaseModel):
    job_id: str
    interviewer_email: Optional[str] = None

class BatchProcessResponse(BaseModel):
    status: str
    job_id: str
    total_resumes: int
    successfully_parsed: int
    ranked_candidates: List[CandidateResponse]
    processing_summary: dict

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_resumes(
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload candidate resumes
    
    Accepts multiple PDF or DOCX files
    """
    logger.info(f"User {current_user.get('email')} uploading {len(files)} resumes")
    
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )
    
    uploaded_files = []
    errors = []
    
    for file in files:
        try:
            # Validate file type
            if not file.filename.lower().endswith(('.pdf', '.docx')):
                errors.append({
                    "filename": file.filename,
                    "error": "Invalid file type. Only PDF and DOCX are supported"
                })
                continue
            
            # Validate file size (max 10MB)
            file.file.seek(0, 2)  # Seek to end
            file_size = file.file.tell()
            file.file.seek(0)  # Reset to beginning
            
            if file_size > 10 * 1024 * 1024:  # 10MB
                errors.append({
                    "filename": file.filename,
                    "error": "File size exceeds 10MB limit"
                })
                continue
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{file.filename}"
            
            # Save file
            file_path = os.path.join(config.RESUME_STORAGE_PATH, unique_filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append({
                "original_filename": file.filename,
                "stored_filename": unique_filename,
                "file_path": file_path,
                "file_size": file_size,
                "uploaded_at": datetime.now().isoformat()
            })
            
            logger.info(f"Successfully uploaded: {file.filename}")
            
        except Exception as e:
            logger.error(f"Error uploading {file.filename}: {str(e)}")
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "status": "success",
        "uploaded_count": len(uploaded_files),
        "error_count": len(errors),
        "uploaded_files": uploaded_files,
        "errors": errors if errors else None
    }

@router.post("/process-batch", status_code=status.HTTP_200_OK)
async def process_batch(
    request: BatchProcessRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Process a batch of uploaded resumes for a specific job
    
    This will parse resumes, match skills, analyze cultural fit, and rank candidates
    """
    logger.info(f"Processing batch for job {request.job_id}")
    
    try:
        # Get all resumes from storage
        resume_dir = config.RESUME_STORAGE_PATH
        
        if not os.path.exists(resume_dir):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No resumes found"
            )
        
        resume_files = [
            f for f in os.listdir(resume_dir) 
            if f.endswith(('.pdf', '.docx'))
        ]
        
        if not resume_files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No resumes found to process"
            )
        
        # Extract text from resumes
        resumes = []
        for filename in resume_files:
            file_path = os.path.join(resume_dir, filename)
            
            try:
                if filename.endswith('.pdf'):
                    text = extract_text_from_pdf(file_path)
                else:
                    text = extract_text_from_docx(file_path)
                
                resumes.append({
                    "filename": filename,
                    "resume_content": text
                })
            except Exception as e:
                logger.error(f"Error extracting text from {filename}: {str(e)}")
                continue
        
        # TODO: Fetch job description from database using request.job_id
        # For now, using a mock job description
        job_description = {
            "title": "Senior Software Engineer",
            "required_skills": ["Python", "AWS", "Docker", "Kubernetes"],
            "preferred_skills": ["React", "TypeScript", "CI/CD"],
            "experience_level": "Senior (5+ years)",
            "responsibilities": [
                "Design and develop scalable applications",
                "Lead technical discussions",
                "Mentor junior developers"
            ]
        }
        
        # Process through orchestrator
        result = await orchestrator.process({
            "resumes": resumes,
            "job_description": job_description,
            "company_culture": {},
            "interviewer_email": request.interviewer_email
        })
        
        if result["status"] != "success":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("message", "Processing failed")
            )
        
        return {
            "status": "success",
            "job_id": request.job_id,
            "total_resumes": result["processing_summary"]["total_resumes"],
            "successfully_parsed": result["processing_summary"]["successfully_parsed"],
            "ranked_candidates": result["ranked_candidates"],
            "processing_summary": result["processing_summary"],
            "scheduled_interviews": result.get("scheduled_interviews", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing batch: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing batch: {str(e)}"
        )

@router.get("/", response_model=List[CandidateResponse])
async def get_candidates(
    job_id: Optional[str] = None,
    tier: Optional[str] = None,
    min_score: Optional[float] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all candidates with optional filters
    
    Query parameters:
    - job_id: Filter by job ID
    - tier: Filter by tier (strong_match, moderate_match, weak_match)
    - min_score: Filter by minimum overall score
    """
    # TODO: Implement database query
    # For now, return empty list
    logger.info(f"Fetching candidates with filters: job_id={job_id}, tier={tier}, min_score={min_score}")
    
    return []

@router.get("/{candidate_id}")
async def get_candidate(
    candidate_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get specific candidate details including full evaluation
    """
    logger.info(f"Fetching candidate {candidate_id}")
    
    # TODO: Implement database query
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Candidate {candidate_id} not found"
    )

@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
    candidate_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a candidate and their associated data
    """
    logger.info(f"Deleting candidate {candidate_id}")
    
    # TODO: Implement database deletion and file cleanup
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Candidate {candidate_id} not found"
    )

@router.put("/{candidate_id}/tier")
async def update_candidate_tier(
    candidate_id: str,
    tier: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Update candidate tier (for manual override)
    """
    if tier not in ["strong_match", "moderate_match", "weak_match"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tier. Must be one of: strong_match, moderate_match, weak_match"
        )
    
    logger.info(f"Updating candidate {candidate_id} tier to {tier}")
    
    # TODO: Implement database update
    return {
        "status": "success",
        "candidate_id": candidate_id,
        "new_tier": tier
    }