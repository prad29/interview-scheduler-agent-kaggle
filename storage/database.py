"""
Database management and ORM models

This module handles database connections, session management, and ORM models
for storing candidates, jobs, evaluations, and interviews.
"""

from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean, Text, JSON, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import StaticPool
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
import logging

from config import config

logger = logging.getLogger(__name__)

# Create base class for declarative models
Base = declarative_base()

# Create engine and session factory
engine = create_engine(config.DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM Models

class JobModel(Base):
    """Job description ORM model"""
    __tablename__ = 'jobs'
    
    id = Column(String(100), primary_key=True)
    title = Column(String(200), nullable=False)
    department = Column(String(100))
    location = Column(String(200))
    work_location_type = Column(String(50))
    employment_type = Column(String(50))
    experience_level = Column(String(50))
    
    description = Column(Text)
    responsibilities = Column(JSON)  # List of strings
    
    # Requirements stored as JSON
    requirements = Column(JSON)
    
    # Compensation
    salary_min = Column(Float)
    salary_max = Column(Float)
    salary_currency = Column(String(10))
    compensation_range = Column(String(100))
    benefits = Column(JSON)  # List of strings
    
    # Company info
    company_name = Column(String(200))
    company_description = Column(Text)
    company_culture = Column(JSON)
    
    # Additional details
    team_description = Column(Text)
    growth_opportunities = Column(JSON)
    reporting_to = Column(String(100))
    direct_reports = Column(Integer)
    
    # Metadata
    status = Column(String(50), default='active')
    posted_date = Column(DateTime, default=datetime.now)
    closing_date = Column(DateTime)
    created_by = Column(String(100))
    hiring_manager = Column(String(100))
    total_applications = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    candidates = relationship("CandidateModel", back_populates="job")
    evaluations = relationship("EvaluationModel", back_populates="job")
    interviews = relationship("InterviewModel", back_populates="job")


class CandidateModel(Base):
    """Candidate ORM model"""
    __tablename__ = 'candidates'
    
    id = Column(String(100), primary_key=True)
    job_id = Column(String(100), ForeignKey('jobs.id'), nullable=True)
    
    # Personal info stored as JSON
    personal_info = Column(JSON, nullable=False)
    
    # Professional background as JSON
    work_experience = Column(JSON)
    education = Column(JSON)
    
    # Skills and qualifications
    skills = Column(JSON)  # List of strings
    certifications = Column(JSON)
    languages = Column(JSON)
    
    # Additional info
    projects = Column(JSON)
    publications = Column(JSON)
    awards = Column(JSON)
    volunteering = Column(JSON)
    
    # Resume info
    resume_path = Column(String(500))
    resume_filename = Column(String(200))
    
    # Computed fields
    total_years_experience = Column(Float)
    
    # Metadata
    status = Column(String(50), default='new')  # new, screening, interview, offer, hired, rejected
    source = Column(String(100))  # job_board, referral, linkedin, etc.
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    job = relationship("JobModel", back_populates="candidates")
    evaluation = relationship("EvaluationModel", back_populates="candidate", uselist=False)
    interviews = relationship("InterviewModel", back_populates="candidate")


class EvaluationModel(Base):
    """Evaluation result ORM model"""
    __tablename__ = 'evaluations'
    
    id = Column(String(100), primary_key=True)
    candidate_id = Column(String(100), ForeignKey('candidates.id'), nullable=False)
    job_id = Column(String(100), ForeignKey('jobs.id'), nullable=False)
    
    # Scores
    overall_score = Column(Float, nullable=False)
    skills_match_score = Column(Float)
    cultural_fit_score = Column(Float)
    experience_score = Column(Float)
    education_score = Column(Float)
    
    # Skills evaluation stored as JSON
    skills_evaluation = Column(JSON)
    
    # Cultural fit evaluation stored as JSON
    cultural_evaluation = Column(JSON)
    
    # Recommendation
    recommendation = Column(String(50))  # strong_match, moderate_match, weak_match, rejected
    tier = Column(String(50))
    
    # Summary
    executive_summary = Column(Text)
    key_highlights = Column(JSON)
    concerns = Column(JSON)
    
    # Next steps
    recommended_next_steps = Column(JSON)
    interview_focus_areas = Column(JSON)
    
    # Metadata
    evaluated_at = Column(DateTime, default=datetime.now)
    evaluated_by = Column(String(100))
    processing_time_seconds = Column(Float)
    
    # Weights used
    weights = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    candidate = relationship("CandidateModel", back_populates="evaluation")
    job = relationship("JobModel", back_populates="evaluations")


class InterviewModel(Base):
    """Interview slot ORM model"""
    __tablename__ = 'interviews'
    
    id = Column(String(100), primary_key=True)
    candidate_id = Column(String(100), ForeignKey('candidates.id'), nullable=False)
    job_id = Column(String(100), ForeignKey('jobs.id'), nullable=True)
    
    # Candidate info
    candidate_name = Column(String(200), nullable=False)
    candidate_email = Column(String(200), nullable=False)
    candidate_phone = Column(String(50))
    
    # Interview details
    interview_type = Column(String(50))
    round_number = Column(Integer)
    
    # Schedule
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    timezone = Column(String(50), default='UTC')
    
    # Attendees
    interviewer_email = Column(String(200), nullable=False)
    interviewer_name = Column(String(200))
    attendees = Column(JSON)  # List of attendee objects
    
    # Location/Meeting
    meeting_platform = Column(String(50))
    location = Column(String(500))
    video_conference_link = Column(String(500))
    meeting_id = Column(String(200))
    meeting_password = Column(String(100))
    
    # Status
    status = Column(String(50), default='proposed')
    
    # Calendar integration
    calendar_event_id = Column(String(200))
    calendar_link = Column(String(500))
    
    # Interview content
    title = Column(String(500))
    description = Column(Text)
    focus_areas = Column(JSON)
    required_materials = Column(JSON)
    
    # Evaluation
    evaluation_template_id = Column(String(100))
    evaluation_scorecard = Column(JSON)
    
    # Results (post-interview)
    completed_at = Column(DateTime)
    notes = Column(Text)
    rating = Column(Integer)
    recommendation = Column(String(50))
    feedback = Column(Text)
    
    # Reminders
    reminder_sent = Column(Boolean, default=False)
    reminder_sent_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now)
    created_by = Column(String(100))
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    cancelled_at = Column(DateTime)
    cancellation_reason = Column(Text)
    
    # Relationships
    candidate = relationship("CandidateModel", back_populates="interviews")
    job = relationship("JobModel", back_populates="interviews")


class ActivityLogModel(Base):
    """Activity log for audit trail"""
    __tablename__ = 'activity_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Activity details
    activity_type = Column(String(50), nullable=False)  # resume_uploaded, evaluation_completed, interview_scheduled, etc.
    entity_type = Column(String(50))  # candidate, job, interview, etc.
    entity_id = Column(String(100))
    
    # User/agent
    performed_by = Column(String(100))
    is_automated = Column(Boolean, default=False)
    
    # Details
    description = Column(Text)
    details = Column(JSON)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.now)
    ip_address = Column(String(50))


# Database class

class Database:
    """Database management class"""
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize database connection
        
        Args:
            connection_string: Database connection string. If None, uses config.DATABASE_URL
        """
        self.connection_string = connection_string or config.DATABASE_URL
        
        if not self.connection_string:
            logger.warning("No database URL configured. Using in-memory SQLite database.")
            self.connection_string = "sqlite:///:memory:"
            self.engine = create_engine(
                self.connection_string,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=config.DEBUG
            )
        else:
            self.engine = create_engine(
                self.connection_string,
                echo=config.DEBUG
            )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        logger.info(f"Database initialized: {self.connection_string.split('@')[-1] if '@' in self.connection_string else 'in-memory'}")
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise
    
    def drop_tables(self):
        """Drop all database tables (use with caution!)"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Error dropping database tables: {str(e)}")
            raise
    
    def get_session(self) -> Session:
        """
        Get a new database session
        
        Returns:
            SQLAlchemy Session object
        """
        return self.SessionLocal()
    
    def close(self):
        """Close database connection"""
        self.engine.dispose()
        logger.info("Database connection closed")


# Session management helper

_db_instance: Optional[Database] = None

def get_database() -> Database:
    """
    Get or create database instance (singleton pattern)
    
    Returns:
        Database instance
    """
    global _db_instance
    
    if _db_instance is None:
        _db_instance = Database()
        _db_instance.create_tables()
    
    return _db_instance

def get_db_session() -> Session:
    """
    Get a new database session
    
    Yields:
        SQLAlchemy Session object
        
    Usage:
        with get_db_session() as session:
            # Use session
            pass
    """
    db = get_database()
    session = db.get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Helper functions for common operations

def save_job(job_data: Dict[str, Any], session: Session) -> JobModel:
    """Save job to database"""
    job = JobModel(**job_data)
    session.add(job)
    session.commit()
    session.refresh(job)
    return job

def save_candidate(candidate_data: Dict[str, Any], session: Session) -> CandidateModel:
    """Save candidate to database"""
    candidate = CandidateModel(**candidate_data)
    session.add(candidate)
    session.commit()
    session.refresh(candidate)
    return candidate

def save_evaluation(evaluation_data: Dict[str, Any], session: Session) -> EvaluationModel:
    """Save evaluation to database"""
    evaluation = EvaluationModel(**evaluation_data)
    session.add(evaluation)
    session.commit()
    session.refresh(evaluation)
    return evaluation

def save_interview(interview_data: Dict[str, Any], session: Session) -> InterviewModel:
    """Save interview to database"""
    interview = InterviewModel(**interview_data)
    session.add(interview)
    session.commit()
    session.refresh(interview)
    return interview

def log_activity(
    activity_type: str,
    entity_type: str,
    entity_id: str,
    description: str,
    performed_by: str = "system",
    is_automated: bool = True,
    details: Optional[Dict[str, Any]] = None,
    session: Session = None
):
    """Log activity to audit trail"""
    close_session = False
    
    if session is None:
        db = get_database()
        session = db.get_session()
        close_session = True
    
    try:
        log = ActivityLogModel(
            activity_type=activity_type,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            performed_by=performed_by,
            is_automated=is_automated,
            details=details
        )
        session.add(log)
        session.commit()
    finally:
        if close_session:
            session.close()


# Query helpers

def get_job_by_id(job_id: str, session: Session) -> Optional[JobModel]:
    """Get job by ID"""
    return session.query(JobModel).filter(JobModel.id == job_id).first()

def get_candidate_by_id(candidate_id: str, session: Session) -> Optional[CandidateModel]:
    """Get candidate by ID"""
    return session.query(CandidateModel).filter(CandidateModel.id == candidate_id).first()

def get_candidates_by_job(job_id: str, session: Session) -> List[CandidateModel]:
    """Get all candidates for a job"""
    return session.query(CandidateModel).filter(CandidateModel.job_id == job_id).all()

def get_evaluation_by_candidate(candidate_id: str, session: Session) -> Optional[EvaluationModel]:
    """Get evaluation for a candidate"""
    return session.query(EvaluationModel).filter(EvaluationModel.candidate_id == candidate_id).first()

def get_interviews_by_candidate(candidate_id: str, session: Session) -> List[InterviewModel]:
    """Get all interviews for a candidate"""
    return session.query(InterviewModel).filter(InterviewModel.candidate_id == candidate_id).all()

def get_active_jobs(session: Session) -> List[JobModel]:
    """Get all active jobs"""
    return session.query(JobModel).filter(JobModel.status == 'active').all()

def get_upcoming_interviews(session: Session) -> List[InterviewModel]:
    """Get all upcoming interviews"""
    return session.query(InterviewModel).filter(
        InterviewModel.start_time > datetime.now(),
        InterviewModel.status.in_(['scheduled', 'confirmed'])
    ).order_by(InterviewModel.start_time).all()


# Initialize database on module import if needed
if config.DATABASE_URL:
    try:
        db = get_database()
        logger.info("Database initialized and ready")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")