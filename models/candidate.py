from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from enum import Enum


class PersonalInfo(BaseModel):
    """Personal information of the candidate"""
    name: str = Field(..., description="Full name of the candidate")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="Current location/address")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    github: Optional[str] = Field(None, description="GitHub profile URL")
    portfolio: Optional[str] = Field(None, description="Portfolio website URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@email.com",
                "phone": "+1-555-0123",
                "location": "San Francisco, CA",
                "linkedin": "https://linkedin.com/in/johndoe",
                "github": "https://github.com/johndoe"
            }
        }


class WorkExperience(BaseModel):
    """Work experience entry"""
    company: str = Field(..., description="Company name")
    role: str = Field(..., description="Job title/role")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM or YYYY)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM or YYYY), 'Present' if current")
    duration_months: Optional[int] = Field(None, description="Duration in months")
    location: Optional[str] = Field(None, description="Job location")
    responsibilities: List[str] = Field(default_factory=list, description="List of responsibilities")
    achievements: List[str] = Field(default_factory=list, description="Key achievements")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    is_current: bool = Field(default=False, description="Is this the current position")
    
    class Config:
        json_schema_extra = {
            "example": {
                "company": "Tech Corp",
                "role": "Senior Software Engineer",
                "start_date": "2020-01",
                "end_date": "Present",
                "duration_months": 48,
                "location": "San Francisco, CA",
                "responsibilities": [
                    "Led team of 5 engineers",
                    "Architected microservices infrastructure"
                ],
                "achievements": [
                    "Reduced deployment time by 60%"
                ],
                "technologies": ["Python", "AWS", "Docker", "Kubernetes"],
                "is_current": True
            }
        }


class Education(BaseModel):
    """Education entry"""
    institution: str = Field(..., description="Educational institution name")
    degree: str = Field(..., description="Degree type (BS, MS, PhD, etc.)")
    field_of_study: Optional[str] = Field(None, description="Major/field of study")
    graduation_date: Optional[str] = Field(None, description="Graduation date (YYYY-MM or YYYY)")
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0, description="GPA (0.0-4.0 scale)")
    honors: List[str] = Field(default_factory=list, description="Academic honors and awards")
    relevant_coursework: List[str] = Field(default_factory=list, description="Relevant courses")
    
    @validator('gpa')
    def validate_gpa(cls, v):
        if v is not None and (v < 0.0 or v > 4.0):
            raise ValueError('GPA must be between 0.0 and 4.0')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "institution": "Massachusetts Institute of Technology",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science",
                "graduation_date": "2018-05",
                "gpa": 3.85,
                "honors": ["Dean's List", "Summa Cum Laude"],
                "relevant_coursework": ["Algorithms", "Machine Learning", "Distributed Systems"]
            }
        }


class Certification(BaseModel):
    """Professional certification"""
    name: str = Field(..., description="Certification name")
    issuing_organization: str = Field(..., description="Organization that issued the certification")
    issue_date: Optional[str] = Field(None, description="Issue date (YYYY-MM)")
    expiry_date: Optional[str] = Field(None, description="Expiry date (YYYY-MM)")
    credential_id: Optional[str] = Field(None, description="Credential ID or license number")
    credential_url: Optional[str] = Field(None, description="URL to verify credential")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "AWS Certified Solutions Architect",
                "issuing_organization": "Amazon Web Services",
                "issue_date": "2023-06",
                "expiry_date": "2026-06",
                "credential_id": "AWS-SA-12345",
                "credential_url": "https://aws.amazon.com/verification/12345"
            }
        }


class Project(BaseModel):
    """Project or portfolio item"""
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    role: Optional[str] = Field(None, description="Role in the project")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM)")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    url: Optional[str] = Field(None, description="Project URL or repository")
    highlights: List[str] = Field(default_factory=list, description="Key highlights or achievements")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "E-commerce Platform",
                "description": "Built a scalable e-commerce platform serving 1M+ users",
                "role": "Lead Developer",
                "start_date": "2022-01",
                "end_date": "2023-06",
                "technologies": ["React", "Node.js", "PostgreSQL", "Redis"],
                "url": "https://github.com/johndoe/ecommerce",
                "highlights": [
                    "Handled 10K concurrent users",
                    "Achieved 99.9% uptime"
                ]
            }
        }


class Candidate(BaseModel):
    """Complete candidate profile"""
    id: Optional[str] = Field(None, description="Unique candidate identifier")
    personal_info: PersonalInfo = Field(..., description="Personal information")
    
    # Professional background
    work_experience: List[WorkExperience] = Field(
        default_factory=list,
        description="Work experience history"
    )
    education: List[Education] = Field(
        default_factory=list,
        description="Educational background"
    )
    
    # Skills and qualifications
    skills: List[str] = Field(
        default_factory=list,
        description="Technical and soft skills"
    )
    certifications: List[Certification] = Field(
        default_factory=list,
        description="Professional certifications"
    )
    languages: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Languages and proficiency levels"
    )
    
    # Additional information
    projects: List[Project] = Field(
        default_factory=list,
        description="Projects and portfolio items"
    )
    publications: List[str] = Field(
        default_factory=list,
        description="Publications and papers"
    )
    awards: List[str] = Field(
        default_factory=list,
        description="Awards and recognitions"
    )
    volunteering: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Volunteer experience"
    )
    
    # Metadata
    resume_path: Optional[str] = Field(None, description="Path to resume file")
    resume_filename: Optional[str] = Field(None, description="Original resume filename")
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Timestamp when candidate was created"
    )
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Timestamp when candidate was last updated"
    )
    
    # Computed fields
    total_years_experience: Optional[float] = Field(
        None,
        description="Total years of work experience"
    )
    
    def calculate_total_experience(self) -> float:
        """Calculate total years of experience"""
        total_months = sum(
            exp.duration_months or 0 
            for exp in self.work_experience
        )
        return round(total_months / 12, 1)
    
    def get_latest_position(self) -> Optional[WorkExperience]:
        """Get the most recent work experience"""
        if not self.work_experience:
            return None
        
        # Find current position
        current = [exp for exp in self.work_experience if exp.is_current]
        if current:
            return current[0]
        
        # Otherwise return first in list (assumed to be most recent)
        return self.work_experience[0]
    
    def get_highest_education(self) -> Optional[Education]:
        """Get the highest level of education"""
        if not self.education:
            return None
        
        degree_hierarchy = {
            'phd': 5, 'doctorate': 5,
            'master': 4, 'ms': 4, 'mba': 4, 'ma': 4,
            'bachelor': 3, 'bs': 3, 'ba': 3,
            'associate': 2,
            'diploma': 1
        }
        
        def get_degree_level(degree: str) -> int:
            degree_lower = degree.lower()
            for key, value in degree_hierarchy.items():
                if key in degree_lower:
                    return value
            return 0
        
        return max(self.education, key=lambda x: get_degree_level(x.degree))
    
    def to_summary(self) -> Dict[str, Any]:
        """Generate a summary of the candidate"""
        latest_position = self.get_latest_position()
        highest_education = self.get_highest_education()
        
        return {
            'name': self.personal_info.name,
            'email': self.personal_info.email,
            'current_role': latest_position.role if latest_position else None,
            'current_company': latest_position.company if latest_position else None,
            'total_experience_years': self.calculate_total_experience(),
            'highest_degree': highest_education.degree if highest_education else None,
            'institution': highest_education.institution if highest_education else None,
            'top_skills': self.skills[:10],
            'certifications_count': len(self.certifications),
            'projects_count': len(self.projects)
        }
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "candidate_123",
                "personal_info": {
                    "name": "John Doe",
                    "email": "john.doe@email.com",
                    "phone": "+1-555-0123",
                    "location": "San Francisco, CA"
                },
                "work_experience": [
                    {
                        "company": "Tech Corp",
                        "role": "Senior Software Engineer",
                        "start_date": "2020-01",
                        "end_date": "Present",
                        "is_current": True
                    }
                ],
                "education": [
                    {
                        "institution": "MIT",
                        "degree": "Bachelor of Science",
                        "field_of_study": "Computer Science",
                        "graduation_date": "2018"
                    }
                ],
                "skills": ["Python", "AWS", "Docker", "Kubernetes"],
                "total_years_experience": 8.5
            }
        }