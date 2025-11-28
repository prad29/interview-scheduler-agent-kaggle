from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum


class InterviewStatus(str, Enum):
    """Interview status enumeration"""
    PROPOSED = "proposed"
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    RESCHEDULED = "rescheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class InterviewType(str, Enum):
    """Interview type enumeration"""
    PHONE_SCREEN = "phone_screen"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    CULTURAL = "cultural"
    PANEL = "panel"
    ONSITE = "onsite"
    FINAL = "final"


class MeetingPlatform(str, Enum):
    """Video conference platform"""
    GOOGLE_MEET = "google_meet"
    ZOOM = "zoom"
    MICROSOFT_TEAMS = "microsoft_teams"
    PHONE = "phone"
    IN_PERSON = "in_person"


class Attendee(BaseModel):
    """Interview attendee information"""
    email: EmailStr = Field(..., description="Attendee email address")
    name: Optional[str] = Field(None, description="Attendee name")
    role: Optional[str] = Field(None, description="Role (interviewer, candidate, observer)")
    is_required: bool = Field(default=True, description="Whether attendance is required")
    response_status: Optional[str] = Field(
        None,
        description="RSVP status (accepted, declined, tentative, needs_action)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "interviewer@company.com",
                "name": "John Smith",
                "role": "interviewer",
                "is_required": True,
                "response_status": "accepted"
            }
        }


class InterviewSlot(BaseModel):
    """Interview slot with scheduling information"""
    # Identifiers
    id: Optional[str] = Field(None, description="Unique interview slot identifier")
    candidate_id: str = Field(..., description="Candidate identifier")
    job_id: Optional[str] = Field(None, description="Job identifier")
    
    # Candidate information
    candidate_name: str = Field(..., description="Candidate name")
    candidate_email: EmailStr = Field(..., description="Candidate email")
    candidate_phone: Optional[str] = Field(None, description="Candidate phone number")
    
    # Interview details
    interview_type: InterviewType = Field(
        default=InterviewType.TECHNICAL,
        description="Type of interview"
    )
    round_number: Optional[int] = Field(
        None,
        ge=1,
        description="Interview round number"
    )
    
    # Schedule
    start_time: datetime = Field(..., description="Interview start time")
    end_time: datetime = Field(..., description="Interview end time")
    duration_minutes: int = Field(..., ge=15, description="Interview duration in minutes")
    timezone: str = Field(default="UTC", description="Timezone for the interview")
    
    # Attendees
    interviewer_email: EmailStr = Field(..., description="Primary interviewer email")
    interviewer_name: Optional[str] = Field(None, description="Primary interviewer name")
    attendees: List[Attendee] = Field(
        default_factory=list,
        description="All interview attendees"
    )
    
    # Location/Meeting
    meeting_platform: MeetingPlatform = Field(
        ...,
        description="Meeting platform or location type"
    )
    location: Optional[str] = Field(
        None,
        description="Physical location or meeting room"
    )
    video_conference_link: Optional[str] = Field(
        None,
        description="Video conference link"
    )
    meeting_id: Optional[str] = Field(None, description="Meeting ID or dial-in code")
    meeting_password: Optional[str] = Field(None, description="Meeting password")
    
    # Status
    status: InterviewStatus = Field(
        default=InterviewStatus.PROPOSED,
        description="Interview status"
    )
    
    # Calendar integration
    calendar_event_id: Optional[str] = Field(
        None,
        description="Google Calendar event ID"
    )
    calendar_link: Optional[str] = Field(
        None,
        description="Link to calendar event"
    )
    
    # Interview content
    title: Optional[str] = Field(None, description="Interview title")
    description: Optional[str] = Field(None, description="Interview description")
    focus_areas: List[str] = Field(
        default_factory=list,
        description="Areas to focus on during interview"
    )
    required_materials: List[str] = Field(
        default_factory=list,
        description="Materials candidate should prepare"
    )
    
    # Evaluation
    evaluation_template_id: Optional[str] = Field(
        None,
        description="ID of evaluation template to use"
    )
    evaluation_scorecard: Optional[Dict[str, Any]] = Field(
        None,
        description="Evaluation scorecard data"
    )
    
    # Interview results (post-interview)
    completed_at: Optional[datetime] = Field(None, description="When interview was completed")
    notes: Optional[str] = Field(None, description="Interview notes")
    rating: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="Interview rating (1-5)"
    )
    recommendation: Optional[str] = Field(
        None,
        description="Interviewer recommendation (hire, no_hire, maybe)"
    )
    feedback: Optional[str] = Field(None, description="Detailed feedback")
    
    # Reminders
    reminder_sent: bool = Field(default=False, description="Whether reminder was sent")
    reminder_sent_at: Optional[datetime] = Field(None, description="When reminder was sent")
    
    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="When slot was created"
    )
    created_by: Optional[str] = Field(None, description="Who created the slot")
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Last update time"
    )
    cancelled_at: Optional[datetime] = Field(None, description="When interview was cancelled")
    cancellation_reason: Optional[str] = Field(None, description="Reason for cancellation")
    
    @validator('end_time')
    def validate_end_time(cls, v, values):
        """Validate that end time is after start time"""
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v
    
    @validator('duration_minutes')
    def validate_duration(cls, v, values):
        """Validate duration matches start and end times"""
        if 'start_time' in values and 'end_time' in values:
            calculated_duration = int(
                (values['end_time'] - values['start_time']).total_seconds() / 60
            )
            if abs(calculated_duration - v) > 1:  # Allow 1 minute tolerance
                raise ValueError(
                    f'duration_minutes ({v}) does not match start and end times ({calculated_duration})'
                )
        return v
    
    def is_upcoming(self) -> bool:
        """Check if interview is upcoming"""
        return (
            self.start_time > datetime.now() and
            self.status in [InterviewStatus.SCHEDULED, InterviewStatus.CONFIRMED]
        )
    
    def is_past(self) -> bool:
        """Check if interview is in the past"""
        return self.end_time < datetime.now()
    
    def can_be_rescheduled(self) -> bool:
        """Check if interview can be rescheduled"""
        return self.status in [
            InterviewStatus.PROPOSED,
            InterviewStatus.SCHEDULED,
            InterviewStatus.CONFIRMED
        ]
    
    def get_duration_display(self) -> str:
        """Get human-readable duration"""
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
        return f"{minutes}m"
    
    def add_attendee(self, email: str, name: Optional[str] = None, role: Optional[str] = None):
        """Add an attendee to the interview"""
        attendee = Attendee(email=email, name=name, role=role)
        if attendee not in self.attendees:
            self.attendees.append(attendee)
    
    def to_calendar_event(self) -> Dict[str, Any]:
        """Convert to calendar event format"""
        return {
            'summary': self.title or f"Interview with {self.candidate_name}",
            'description': self.description or '',
            'start': {
                'dateTime': self.start_time.isoformat(),
                'timeZone': self.timezone
            },
            'end': {
                'dateTime': self.end_time.isoformat(),
                'timeZone': self.timezone
            },
            'attendees': [
                {'email': self.candidate_email, 'displayName': self.candidate_name},
                {'email': self.interviewer_email, 'displayName': self.interviewer_name}
            ] + [
                {'email': att.email, 'displayName': att.name}
                for att in self.attendees
            ],
            'location': self.location,
            'conferenceData': {
                'createRequest': {
                    'requestId': f"interview-{self.id or 'new'}"
                }
            } if self.meeting_platform == MeetingPlatform.GOOGLE_MEET else None
        }
    
    def to_summary(self) -> Dict[str, Any]:
        """Generate a summary of the interview"""
        return {
            'id': self.id,
            'candidate_name': self.candidate_name,
            'candidate_email': self.candidate_email,
            'interview_type': self.interview_type.value,
            'start_time': self.start_time.isoformat(),
            'duration': self.get_duration_display(),
            'status': self.status.value,
            'interviewer': self.interviewer_name or self.interviewer_email,
            'location': self.video_conference_link or self.location or 'TBD'
        }
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "interview_123",
                "candidate_id": "candidate_456",
                "job_id": "job_789",
                "candidate_name": "John Doe",
                "candidate_email": "john.doe@email.com",
                "interview_type": "technical",
                "round_number": 1,
                "start_time": "2024-12-15T10:00:00Z",
                "end_time": "2024-12-15T11:00:00Z",
                "duration_minutes": 60,
                "interviewer_email": "interviewer@company.com",
                "interviewer_name": "Jane Smith",
                "meeting_platform": "google_meet",
                "video_conference_link": "https://meet.google.com/abc-defg-hij",
                "status": "scheduled",
                "focus_areas": ["System design", "Algorithms", "Code quality"]
            }
        }