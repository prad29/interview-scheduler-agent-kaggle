"""
Data Validators

Validation functions for candidate data, job descriptions, and other inputs.
"""

import re
from typing import Dict, Any, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    # RFC 5322 simplified pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    return bool(re.match(pattern, email.strip()))


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format
    
    Accepts various formats:
    - +1-555-123-4567
    - (555) 123-4567
    - 555.123.4567
    - 5551234567
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    # Remove country code if present
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    
    # Check if it's all digits and has reasonable length
    return cleaned.isdigit() and 10 <= len(cleaned) <= 15


def validate_url(url: str) -> bool:
    """
    Validate URL format
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    
    return bool(re.match(pattern, url.strip()))


def validate_resume_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate parsed resume data
    
    Args:
        data: Resume data dictionary
        
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    
    if not isinstance(data, dict):
        return False, ["Resume data must be a dictionary"]
    
    # Check personal info
    if 'personal_info' not in data:
        errors.append("Missing personal_info section")
    else:
        personal = data['personal_info']
        
        if not isinstance(personal, dict):
            errors.append("personal_info must be a dictionary")
        else:
            # Check required fields
            if not personal.get('name'):
                errors.append("Missing candidate name in personal_info")
            
            if 'email' in personal:
                if not validate_email(personal['email']):
                    errors.append(f"Invalid email format: {personal.get('email')}")
            else:
                errors.append("Missing email address in personal_info")
            
            # Check optional fields
            if 'phone' in personal and personal['phone']:
                if not validate_phone(personal['phone']):
                    errors.append(f"Invalid phone format: {personal.get('phone')}")
            
            if 'linkedin' in personal and personal['linkedin']:
                if not validate_url(personal['linkedin']):
                    errors.append(f"Invalid LinkedIn URL: {personal.get('linkedin')}")
            
            if 'github' in personal and personal['github']:
                if not validate_url(personal['github']):
                    errors.append(f"Invalid GitHub URL: {personal.get('github')}")
    
    # Check work experience
    if 'work_experience' in data:
        if not isinstance(data['work_experience'], list):
            errors.append("work_experience must be a list")
        else:
            for idx, exp in enumerate(data['work_experience']):
                if not isinstance(exp, dict):
                    errors.append(f"work_experience[{idx}] must be a dictionary")
                    continue
                
                if not exp.get('company'):
                    errors.append(f"work_experience[{idx}] missing company name")
                
                if not exp.get('role'):
                    errors.append(f"work_experience[{idx}] missing role/title")
    
    # Check education
    if 'education' in data:
        if not isinstance(data['education'], list):
            errors.append("education must be a list")
        else:
            for idx, edu in enumerate(data['education']):
                if not isinstance(edu, dict):
                    errors.append(f"education[{idx}] must be a dictionary")
                    continue
                
                if not edu.get('institution'):
                    errors.append(f"education[{idx}] missing institution")
                
                if not edu.get('degree'):
                    errors.append(f"education[{idx}] missing degree")
    
    # Check skills
    if 'skills' in data:
        if not isinstance(data['skills'], list):
            errors.append("skills must be a list")
        else:
            if len(data['skills']) == 0:
                logger.warning("No skills found in resume data")
    
    # Check certifications
    if 'certifications' in data:
        if not isinstance(data['certifications'], list):
            errors.append("certifications must be a list")
    
    return (len(errors) == 0, errors)


def validate_job_description(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate job description data
    
    Args:
        data: Job description dictionary
        
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    
    if not isinstance(data, dict):
        return False, ["Job description must be a dictionary"]
    
    # Required fields
    required_fields = ['title']
    
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Missing required field: {field}")
    
    # Validate requirements if present
    if 'requirements' in data:
        req = data['requirements']
        
        if isinstance(req, dict):
            # Validate required_skills
            if 'required_skills' in req:
                if not isinstance(req['required_skills'], list):
                    errors.append("requirements.required_skills must be a list")
                elif len(req['required_skills']) == 0:
                    errors.append("requirements.required_skills cannot be empty")
            
            # Validate preferred_skills
            if 'preferred_skills' in req:
                if not isinstance(req['preferred_skills'], list):
                    errors.append("requirements.preferred_skills must be a list")
            
            # Validate experience years
            if 'required_experience_years' in req:
                years = req['required_experience_years']
                if not isinstance(years, (int, float)) or years < 0:
                    errors.append("requirements.required_experience_years must be a non-negative number")
        else:
            errors.append("requirements must be a dictionary")
    
    # Validate required_skills at top level (alternative format)
    if 'required_skills' in data:
        if not isinstance(data['required_skills'], list):
            errors.append("required_skills must be a list")
        elif len(data['required_skills']) == 0:
            logger.warning("No required skills specified")
    
    # Validate preferred_skills at top level
    if 'preferred_skills' in data:
        if not isinstance(data['preferred_skills'], list):
            errors.append("preferred_skills must be a list")
    
    # Validate responsibilities
    if 'responsibilities' in data:
        if not isinstance(data['responsibilities'], list):
            errors.append("responsibilities must be a list")
    
    # Validate company_culture
    if 'company_culture' in data:
        if not isinstance(data['company_culture'], dict):
            errors.append("company_culture must be a dictionary")
    
    return (len(errors) == 0, errors)


def validate_candidate_score(score: float) -> bool:
    """
    Validate that a score is in valid range (0.0 to 1.0)
    
    Args:
        score: Score to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(score, (int, float)):
        return False
    
    return 0.0 <= score <= 1.0


def validate_evaluation_result(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate evaluation result data
    
    Args:
        data: Evaluation result dictionary
        
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    
    # Required fields
    required_fields = ['candidate_id', 'job_id', 'overall_score']
    
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Validate scores
    score_fields = ['overall_score', 'skills_match_score', 'cultural_fit_score', 'experience_score']
    
    for field in score_fields:
        if field in data:
            score = data[field]
            
            # Allow both 0-1 and 0-100 ranges
            if isinstance(score, (int, float)):
                if not (0 <= score <= 1 or 0 <= score <= 100):
                    errors.append(f"{field} must be between 0-1 or 0-100")
            else:
                errors.append(f"{field} must be a number")
    
    # Validate recommendation
    if 'recommendation' in data:
        valid_recommendations = ['strong_match', 'moderate_match', 'weak_match', 'rejected']
        if data['recommendation'] not in valid_recommendations:
            errors.append(f"Invalid recommendation. Must be one of: {valid_recommendations}")
    
    return (len(errors) == 0, errors)


def validate_interview_slot(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate interview slot data
    
    Args:
        data: Interview slot dictionary
        
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    
    # Required fields
    required_fields = ['candidate_id', 'candidate_name', 'candidate_email', 'interviewer_email']
    
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Missing required field: {field}")
    
    # Validate emails
    for email_field in ['candidate_email', 'interviewer_email']:
        if email_field in data and data[email_field]:
            if not validate_email(data[email_field]):
                errors.append(f"Invalid email format for {email_field}")
    
    # Validate duration
    if 'duration_minutes' in data:
        duration = data['duration_minutes']
        if not isinstance(duration, int) or duration < 15:
            errors.append("duration_minutes must be an integer >= 15")
    
    # Validate status
    if 'status' in data:
        valid_statuses = ['proposed', 'scheduled', 'confirmed', 'completed', 'cancelled', 'no_show']
        if data['status'] not in valid_statuses:
            errors.append(f"Invalid status. Must be one of: {valid_statuses}")
    
    return (len(errors) == 0, errors)


def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize text input by removing potentially harmful content
    
    Args:
        text: Text to sanitize
        max_length: Maximum length to truncate to
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove null bytes
    sanitized = text.replace('\x00', '')
    
    # Normalize whitespace
    sanitized = ' '.join(sanitized.split())
    
    # Truncate if needed
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...'
    
    return sanitized


def validate_date_format(date_str: str) -> bool:
    """
    Validate date string format (YYYY-MM or YYYY)
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not date_str or not isinstance(date_str, str):
        return False
    
    # Allow "Present" or "Current"
    if date_str.lower() in ['present', 'current']:
        return True
    
    # YYYY-MM format
    if re.match(r'^\d{4}-\d{2}$', date_str):
        return True
    
    # YYYY format
    if re.match(r'^\d{4}$', date_str):
        return True
    
    return False