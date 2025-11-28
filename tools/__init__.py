"""
Tools package for utility functions and integrations

This package provides various utility tools for the recruitment system:
- Document parsers (PDF, DOCX)
- Calendar integration (Google Calendar)
- Email service
- Data validators
"""

from .pdf_parser import extract_text_from_pdf
from .docx_parser import extract_text_from_docx
from .calendar_integration import CalendarService
from .email_service import EmailService
from .data_validator import (
    validate_resume_data,
    validate_job_description,
    validate_email,
    validate_phone,
    validate_candidate_score
)

__all__ = [
    # Document parsers
    'extract_text_from_pdf',
    'extract_text_from_docx',
    
    # Services
    'CalendarService',
    'EmailService',
    
    # Validators
    'validate_resume_data',
    'validate_job_description',
    'validate_email',
    'validate_phone',
    'validate_candidate_score'
]

__version__ = '1.0.0'