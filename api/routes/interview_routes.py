from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
import logging

from api.middleware.auth import get_current_user
from agents.interview_scheduler_agent import InterviewSchedulerAgent

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize scheduler
scheduler_agent = InterviewSchedulerAgent()

# Pydantic models
class InterviewScheduleRequest(BaseModel):
    candidate_id: str
    interviewer_email: EmailStr
    duration_minutes: int = 60
    preferred_dates: Optional[List[str]] = None

class InterviewResponse(BaseModel):
    id: str
    candidate_id: str
    candidate_name: str
    candidate_email: str
    interviewer_email: str
    start_time: str
    end_time: str
    status: str
    calendar_event_id: Optional[str]
    created_at: str

class InterviewUpdate(BaseModel):
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

@router.post("/schedule", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def schedule_interview(
    request: InterviewScheduleRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Schedule an interview for a candidate
    """
    logger.info(f"Scheduling interview for candidate {request.candidate_id}")
    
    try:
        # TODO: Fetch candidate details from database
        candidate = {
            "id": request.candidate_id,
            "name": "John Doe",  # Placeholder
            "email": "john.doe@example.com"  # Placeholder
        }
        
        # Schedule using agent
        result = await scheduler_agent.process({
            "candidates": [candidate],
            "interviewer_email": request.interviewer_email,
            "duration_minutes": request.duration_minutes
        })
        
        if result["status"] != "success" or not result["scheduled_slots"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to schedule interview. No available slots found."
            )
        
        scheduled_slot = result["scheduled_slots"][0]
        
        # TODO: Save to database
        interview_id = f"interview_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        interview_response = InterviewResponse(
            id=interview_id,
            candidate_id=scheduled_slot["candidate_id"],
            candidate_name=scheduled_slot["candidate_name"],
            candidate_email=scheduled_slot["candidate_email"],
            interviewer_email=request.interviewer_email,
            start_time=scheduled_slot["start_time"],
            end_time=scheduled_slot["end_time"],
            status=scheduled_slot["status"],
            calendar_event_id=scheduled_slot.get("calendar_event_id"),
            created_at=datetime.now().isoformat()
        )
        
        logger.info(f"Interview scheduled successfully: {interview_id}")
        return interview_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scheduling interview: {str(e)}"
        )

@router.get("/", response_model=List[InterviewResponse])
async def get_interviews(
    status_filter: Optional[str] = None,
    candidate_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all scheduled interviews with optional filters
    
    Query parameters:
    - status_filter: Filter by status (scheduled, completed, cancelled)
    - candidate_id: Filter by candidate
    - start_date: Filter interviews after this date (ISO format)
    - end_date: Filter interviews before this date (ISO format)
    """
    logger.info(f"Fetching interviews with filters")
    
    # TODO: Implement database query
    return []

@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get specific interview details
    """
    logger.info(f"Fetching interview {interview_id}")
    
    # TODO: Implement database query
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Interview {interview_id} not found"
    )

@router.put("/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: str,
    interview_update: InterviewUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update interview details (reschedule, change status, add notes)
    """
    logger.info(f"Updating interview {interview_id}")
    
    if interview_update.status and interview_update.status not in [
        "scheduled", "confirmed", "completed", "cancelled", "rescheduled"
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status value"
        )
    
    # TODO: Implement database update
    # TODO: Update calendar event if time changed
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Interview {interview_id} not found"
    )

@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_interview(
    interview_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Cancel an interview
    """
    logger.info(f"Cancelling interview {interview_id}")
    
    # TODO: Implement cancellation
    # TODO: Delete calendar event
    # TODO: Send cancellation email
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Interview {interview_id} not found"
    )

@router.post("/{interview_id}/reschedule")
async def reschedule_interview(
    interview_id: str,
    new_start_time: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Reschedule an existing interview
    """
    logger.info(f"Rescheduling interview {interview_id}")
    
    try:
        # Parse new time
        new_datetime = datetime.fromisoformat(new_start_time)
        
        # TODO: Check availability
        # TODO: Update calendar event
        # TODO: Send reschedule notification
        
        return {
            "status": "success",
            "message": "Interview rescheduled successfully",
            "interview_id": interview_id,
            "new_start_time": new_start_time
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        )
    except Exception as e:
        logger.error(f"Error rescheduling interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error rescheduling interview: {str(e)}"
        )

@router.post("/{interview_id}/complete")
async def complete_interview(
    interview_id: str,
    notes: Optional[str] = None,
    rating: Optional[int] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark an interview as completed with optional notes and rating
    """
    logger.info(f"Marking interview {interview_id} as completed")
    
    if rating and (rating < 1 or rating > 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
    
    # TODO: Update interview status
    # TODO: Save notes and rating
    
    return {
        "status": "success",
        "message": "Interview marked as completed",
        "interview_id": interview_id
    }