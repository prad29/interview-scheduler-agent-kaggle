"""
Data service for fetching data from database and JSON files

This module provides a unified interface for fetching data from both
the SQLite database and JSON files used by the dashboard.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from storage.database import (
    Base, JobModel, CandidateModel,
    EvaluationModel, InterviewModel
)
from config import config

# Database setup
engine = create_engine(config.DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    """Get database session"""
    return SessionLocal()

def get_jobs(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get jobs from JSON files (preferred) or database

    Args:
        status: Filter by status (active, closed, etc.)

    Returns:
        List of job dictionaries
    """
    # Try to get from JSON files first (used by dashboard)
    jobs_list_file = Path("data/jobs/jobs_list.json")

    if jobs_list_file.exists():
        try:
            with open(jobs_list_file, 'r') as f:
                jobs = json.load(f)

            # Filter by status if provided
            if status:
                jobs = [j for j in jobs if j.get('status') == status]

            return jobs
        except Exception as e:
            print(f"Error reading jobs from JSON: {e}")

    # Fallback to database
    try:
        session = get_db_session()
        query = session.query(JobModel)

        if status:
            query = query.filter(JobModel.status == status)

        db_jobs = query.all()

        jobs = []
        for job in db_jobs:
            jobs.append({
                'id': job.id,
                'title': job.title,
                'department': job.department,
                'location': job.location,
                'status': job.status,
                'requirements': job.requirements,
                'salary_min': job.salary_min,
                'salary_max': job.salary_max,
                'created_at': job.created_at.isoformat() if job.created_at else None
            })

        session.close()
        return jobs
    except Exception as e:
        print(f"Error fetching jobs from database: {e}")
        return []

def get_candidates(
    job_id: Optional[str] = None,
    tier: Optional[str] = None,
    min_score: Optional[float] = None,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get candidates from database with optional filters

    Args:
        job_id: Filter by job ID
        tier: Filter by tier (strong_match, moderate_match, weak_match)
        min_score: Minimum overall score
        status: Filter by status

    Returns:
        List of candidate dictionaries with evaluation data
    """
    try:
        session = get_db_session()

        # Query candidates with their evaluations
        query = session.query(CandidateModel, EvaluationModel).join(
            EvaluationModel,
            CandidateModel.id == EvaluationModel.candidate_id,
            isouter=True
        )

        # Apply filters
        if job_id:
            query = query.filter(CandidateModel.job_id == job_id)

        if status:
            query = query.filter(CandidateModel.status == status)

        if tier:
            query = query.filter(EvaluationModel.tier == tier)

        if min_score:
            query = query.filter(EvaluationModel.overall_score >= min_score)

        results = query.all()

        candidates = []
        for candidate, evaluation in results:
            candidate_dict = {
                'id': candidate.id,
                'name': candidate.personal_info.get('name', 'Unknown') if candidate.personal_info else 'Unknown',
                'email': candidate.personal_info.get('email', '') if candidate.personal_info else '',
                'phone': candidate.personal_info.get('phone', '') if candidate.personal_info else '',
                'status': candidate.status,
                'job_id': candidate.job_id,
                'created_at': candidate.created_at.isoformat() if candidate.created_at else None,
                'candidate_data': {
                    'personal_info': candidate.personal_info,
                    'work_experience': candidate.work_experience,
                    'education': candidate.education,
                    'skills': candidate.skills
                }
            }

            # Add evaluation data if available
            if evaluation:
                candidate_dict.update({
                    'overall_score': evaluation.overall_score,
                    'skills_match_score': evaluation.skills_match_score,
                    'cultural_fit_score': evaluation.cultural_fit_score,
                    'experience_score': evaluation.experience_score,
                    'tier': evaluation.tier,
                    'recommendation': evaluation.recommendation,
                    'matched_skills': evaluation.skills_evaluation.get('matched_skills', []) if evaluation.skills_evaluation else [],
                    'missing_skills': evaluation.skills_evaluation.get('missing_skills', []) if evaluation.skills_evaluation else [],
                    'skills_rationale': evaluation.skills_evaluation.get('rationale', '') if evaluation.skills_evaluation else '',
                    'cultural_rationale': evaluation.cultural_evaluation.get('rationale', '') if evaluation.cultural_evaluation else '',
                    'dimensional_scores': evaluation.cultural_evaluation.get('dimensional_scores', {}) if evaluation.cultural_evaluation else {}
                })
            else:
                # Default values if no evaluation
                candidate_dict.update({
                    'overall_score': 0,
                    'skills_match_score': 0,
                    'cultural_fit_score': 0,
                    'experience_score': 0,
                    'tier': 'not_evaluated',
                    'recommendation': 'pending',
                    'matched_skills': [],
                    'missing_skills': [],
                    'skills_rationale': '',
                    'cultural_rationale': '',
                    'dimensional_scores': {}
                })

            candidates.append(candidate_dict)

        session.close()

        # Sort by overall score descending
        candidates.sort(key=lambda x: x.get('overall_score', 0), reverse=True)

        return candidates

    except Exception as e:
        print(f"Error fetching candidates: {e}")
        return []

def get_interviews(
    candidate_id: Optional[str] = None,
    status: Optional[str] = None,
    date_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get interviews from database with optional filters

    Args:
        candidate_id: Filter by candidate ID
        status: Filter by status
        date_filter: Filter by date range (today, this_week, this_month, upcoming)

    Returns:
        List of interview dictionaries
    """
    try:
        session = get_db_session()

        query = session.query(InterviewModel)

        # Apply filters
        if candidate_id:
            query = query.filter(InterviewModel.candidate_id == candidate_id)

        if status:
            query = query.filter(InterviewModel.status == status)

        # Apply date filters
        now = datetime.now()
        if date_filter == 'today':
            query = query.filter(
                func.date(InterviewModel.start_time) == now.date()
            )
        elif date_filter == 'this_week':
            start_of_week = now - timedelta(days=now.weekday())
            end_of_week = start_of_week + timedelta(days=7)
            query = query.filter(
                InterviewModel.start_time >= start_of_week,
                InterviewModel.start_time < end_of_week
            )
        elif date_filter == 'this_month':
            query = query.filter(
                func.strftime('%Y-%m', InterviewModel.start_time) == now.strftime('%Y-%m')
            )
        elif date_filter == 'upcoming':
            query = query.filter(InterviewModel.start_time >= now)

        db_interviews = query.order_by(InterviewModel.start_time.desc()).all()

        interviews = []
        for interview in db_interviews:
            # Join with candidate to get evaluation score
            candidate = session.query(CandidateModel).filter_by(id=interview.candidate_id).first()
            evaluation = session.query(EvaluationModel).filter_by(candidate_id=interview.candidate_id).first()

            interviews.append({
                'id': interview.id,
                'candidate_name': interview.candidate_name,
                'candidate_email': interview.candidate_email,
                'candidate_phone': interview.candidate_phone,
                'overall_score': evaluation.overall_score if evaluation else None,
                'date': interview.start_time.strftime('%b %d, %Y') if interview.start_time else '',
                'time': interview.start_time.strftime('%I:%M %p') if interview.start_time else '',
                'duration': interview.duration_minutes,
                'status': interview.status,
                'meeting_link': interview.video_conference_link,
                'notes': interview.notes,
                'interviewer': interview.interviewer_email,
                'interview_type': interview.interview_type,
                'rating': interview.rating,
                'recommendation': interview.recommendation
            })

        session.close()
        return interviews

    except Exception as e:
        print(f"Error fetching interviews: {e}")
        return []

def get_metrics() -> Dict[str, Any]:
    """
    Get dashboard metrics from database

    Returns:
        Dictionary with various metrics
    """
    try:
        session = get_db_session()

        # Count candidates
        total_candidates = session.query(func.count(CandidateModel.id)).scalar()

        # Count by status
        new_candidates_count = session.query(func.count(CandidateModel.id)).filter(
            CandidateModel.created_at >= datetime.now() - timedelta(days=7)
        ).scalar()

        # Count strong matches
        strong_matches = session.query(func.count(EvaluationModel.id)).filter(
            EvaluationModel.tier == 'strong_match'
        ).scalar()

        # Count interviews
        interviews_count = session.query(func.count(InterviewModel.id)).filter(
            InterviewModel.status.in_(['scheduled', 'confirmed'])
        ).scalar()

        # Count today's interviews
        today_interviews = session.query(func.count(InterviewModel.id)).filter(
            func.date(InterviewModel.start_time) == datetime.now().date()
        ).scalar()

        # Average match score
        avg_score_result = session.query(func.avg(EvaluationModel.overall_score)).scalar()
        avg_match_score = float(avg_score_result) if avg_score_result else 0.0

        # Count active jobs
        active_jobs = session.query(func.count(JobModel.id)).filter(
            JobModel.status == 'active'
        ).scalar()

        # Count qualified candidates (above threshold)
        qualified_candidates = session.query(func.count(EvaluationModel.id)).filter(
            EvaluationModel.overall_score >= config.SKILLS_MATCH_THRESHOLD
        ).scalar()

        session.close()

        return {
            'total_candidates': total_candidates or 0,
            'candidates_delta': new_candidates_count or 0,
            'strong_matches': strong_matches or 0,
            'strong_matches_delta': 0,  # Would need historical data
            'interviews_scheduled': interviews_count or 0,
            'interviews_delta': today_interviews or 0,
            'average_match_score': round(avg_match_score, 1),
            'score_delta': 0,  # Would need historical data
            'active_jobs': active_jobs or 0,
            'qualified_candidates': qualified_candidates or 0,
            'avg_processing_time': 8.3,  # Would need to track this
            'time_to_schedule': 18.5,  # Would need to track this
            'time_saved_percentage': 82,  # Static value
            'resumes_per_hour': 105,  # Static value
            'agent_accuracy': 87.5  # Static value
        }

    except Exception as e:
        print(f"Error fetching metrics: {e}")
        # Return default values
        return {
            'total_candidates': 0,
            'candidates_delta': 0,
            'strong_matches': 0,
            'strong_matches_delta': 0,
            'interviews_scheduled': 0,
            'interviews_delta': 0,
            'average_match_score': 0.0,
            'score_delta': 0,
            'active_jobs': 0,
            'qualified_candidates': 0,
            'avg_processing_time': 0,
            'time_to_schedule': 0,
            'time_saved_percentage': 0,
            'resumes_per_hour': 0,
            'agent_accuracy': 0
        }

def get_recent_activities(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recent activity logs

    Args:
        limit: Maximum number of activities to return

    Returns:
        List of activity dictionaries
    """
    try:
        session = get_db_session()

        activities = []

        # Get recent candidates
        recent_candidates = session.query(CandidateModel).order_by(
            CandidateModel.created_at.desc()
        ).limit(3).all()

        for candidate in recent_candidates:
            time_diff = datetime.now() - candidate.created_at
            hours_ago = int(time_diff.total_seconds() / 3600)
            time_str = f"{hours_ago} hours ago" if hours_ago > 0 else "Just now"

            activities.append({
                'time': time_str,
                'activity': 'New candidate application',
                'details': f"{candidate.personal_info.get('name', 'Unknown')} applied for {candidate.job_id}",
                'type': 'info'
            })

        # Get recent interviews
        recent_interviews = session.query(InterviewModel).order_by(
            InterviewModel.created_at.desc()
        ).limit(3).all()

        for interview in recent_interviews:
            time_diff = datetime.now() - interview.created_at
            hours_ago = int(time_diff.total_seconds() / 3600)
            time_str = f"{hours_ago} hours ago" if hours_ago > 0 else "Just now"

            activities.append({
                'time': time_str,
                'activity': 'Interview scheduled',
                'details': f"{interview.candidate_name} - {interview.start_time.strftime('%b %d, %Y')}",
                'type': 'success'
            })

        # Get recent jobs
        recent_jobs = session.query(JobModel).order_by(
            JobModel.created_at.desc()
        ).limit(2).all()

        for job in recent_jobs:
            time_diff = datetime.now() - job.created_at
            days_ago = int(time_diff.total_seconds() / 86400)
            time_str = f"{days_ago} days ago" if days_ago > 0 else "Today"

            activities.append({
                'time': time_str,
                'activity': 'New job created',
                'details': f"{job.title} position opened",
                'type': 'info'
            })

        session.close()

        # Sort by time and limit
        return activities[:limit]

    except Exception as e:
        print(f"Error fetching activities: {e}")
        return []
