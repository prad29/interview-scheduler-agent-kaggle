from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ExperienceLevel(str, Enum):
    """Experience level enumeration"""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"
    EXECUTIVE = "executive"


class EmploymentType(str, Enum):
    """Employment type enumeration"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERNSHIP = "internship"


class WorkLocation(str, Enum):
    """Work location type"""
    ONSITE = "onsite"
    REMOTE = "remote"
    HYBRID = "hybrid"


class JobRequirements(BaseModel):
    """Job requirements and qualifications"""
    required_skills: List[str] = Field(
        ...,
        description="Must-have skills and qualifications",
        min_items=1
    )
    preferred_skills: List[str] = Field(
        default_factory=list,
        description="Nice-to-have skills and qualifications"
    )
    required_experience_years: Optional[int] = Field(
        None,
        ge=0,
        description="Minimum years of experience required"
    )
    required_education: Optional[str] = Field(
        None,
        description="Minimum education level required"
    )
    preferred_certifications: List[str] = Field(
        default_factory=list,
        description="Preferred professional certifications"
    )
    language_requirements: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Required languages and proficiency levels"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "required_skills": ["Python", "AWS", "Docker", "Kubernetes"],
                "preferred_skills": ["React", "TypeScript", "CI/CD"],
                "required_experience_years": 5,
                "required_education": "Bachelor's degree in Computer Science or related field",
                "preferred_certifications": ["AWS Certified Solutions Architect"],
                "language_requirements": [
                    {"language": "English", "level": "Fluent"}
                ]
            }
        }


class CompanyCulture(BaseModel):
    """Company culture and values"""
    values: List[str] = Field(
        default_factory=list,
        description="Company core values"
    )
    work_style: Optional[str] = Field(
        None,
        description="Work style description (e.g., collaborative, autonomous)"
    )
    team_size: Optional[int] = Field(
        None,
        ge=1,
        description="Team size"
    )
    pace: Optional[str] = Field(
        None,
        description="Work pace (e.g., fast-paced, methodical)"
    )
    innovation_focus: Optional[bool] = Field(
        None,
        description="Whether innovation is a key focus"
    )
    collaboration_level: Optional[str] = Field(
        None,
        description="Level of collaboration (high, medium, low)"
    )
    hierarchy: Optional[str] = Field(
        None,
        description="Organizational hierarchy (flat, structured)"
    )
    mission_driven: Optional[bool] = Field(
        None,
        description="Whether the organization is mission-driven"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "values": ["Innovation", "Collaboration", "Integrity", "Customer Focus"],
                "work_style": "Collaborative with autonomy",
                "team_size": 8,
                "pace": "Fast-paced",
                "innovation_focus": True,
                "collaboration_level": "high",
                "hierarchy": "flat",
                "mission_driven": True
            }
        }


class JobDescription(BaseModel):
    """Complete job description"""
    id: Optional[str] = Field(None, description="Unique job identifier")
    
    # Basic information
    title: str = Field(..., description="Job title")
    department: Optional[str] = Field(None, description="Department or team")
    location: str = Field(..., description="Job location")
    work_location_type: WorkLocation = Field(
        default=WorkLocation.ONSITE,
        description="Work location type (onsite/remote/hybrid)"
    )
    employment_type: EmploymentType = Field(
        default=EmploymentType.FULL_TIME,
        description="Employment type"
    )
    experience_level: ExperienceLevel = Field(
        ...,
        description="Required experience level"
    )
    
    # Job details
    description: str = Field(..., description="Detailed job description")
    responsibilities: List[str] = Field(
        ...,
        description="Key responsibilities",
        min_items=1
    )
    requirements: JobRequirements = Field(..., description="Job requirements")
    
    # Compensation
    salary_min: Optional[float] = Field(None, ge=0, description="Minimum salary")
    salary_max: Optional[float] = Field(None, ge=0, description="Maximum salary")
    salary_currency: Optional[str] = Field(default="USD", description="Salary currency")
    compensation_range: Optional[str] = Field(
        None,
        description="Compensation range as string (e.g., '$100k-$150k')"
    )
    benefits: List[str] = Field(
        default_factory=list,
        description="Benefits and perks"
    )
    
    # Company and culture
    company_name: Optional[str] = Field(None, description="Company name")
    company_description: Optional[str] = Field(None, description="Company description")
    company_culture: Optional[CompanyCulture] = Field(
        None,
        description="Company culture and values"
    )
    
    # Additional details
    team_description: Optional[str] = Field(
        None,
        description="Description of the team"
    )
    growth_opportunities: List[str] = Field(
        default_factory=list,
        description="Career growth opportunities"
    )
    reporting_to: Optional[str] = Field(
        None,
        description="Position this role reports to"
    )
    direct_reports: Optional[int] = Field(
        None,
        ge=0,
        description="Number of direct reports"
    )
    
    # Metadata
    status: str = Field(
        default="active",
        description="Job status (active, closed, on_hold)"
    )
    posted_date: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Date when job was posted"
    )
    closing_date: Optional[datetime] = Field(
        None,
        description="Application closing date"
    )
    created_by: Optional[str] = Field(
        None,
        description="User who created the job posting"
    )
    hiring_manager: Optional[str] = Field(
        None,
        description="Hiring manager email"
    )
    
    # Application tracking
    total_applications: int = Field(
        default=0,
        ge=0,
        description="Total number of applications received"
    )
    
    @validator('salary_max')
    def validate_salary_range(cls, v, values):
        """Validate that max salary is greater than min salary"""
        if v is not None and 'salary_min' in values and values['salary_min'] is not None:
            if v < values['salary_min']:
                raise ValueError('salary_max must be greater than or equal to salary_min')
        return v
    
    def to_summary(self) -> Dict[str, Any]:
        """Generate a summary of the job"""
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company_name,
            'location': self.location,
            'work_location_type': self.work_location_type.value,
            'experience_level': self.experience_level.value,
            'employment_type': self.employment_type.value,
            'salary_range': self.compensation_range,
            'required_skills': self.requirements.required_skills[:5],
            'status': self.status,
            'total_applications': self.total_applications
        }
    
    def get_all_skills(self) -> List[str]:
        """Get all required and preferred skills"""
        return self.requirements.required_skills + self.requirements.preferred_skills
    
    def matches_skill(self, skill: str) -> bool:
        """Check if a skill matches required or preferred skills"""
        all_skills = [s.lower() for s in self.get_all_skills()]
        return skill.lower() in all_skills
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "job_001",
                "title": "Senior Software Engineer",
                "department": "Engineering",
                "location": "San Francisco, CA",
                "work_location_type": "hybrid",
                "employment_type": "full_time",
                "experience_level": "senior",
                "description": "We are looking for a Senior Software Engineer...",
                "responsibilities": [
                    "Design and develop scalable applications",
                    "Lead technical discussions",
                    "Mentor junior developers"
                ],
                "requirements": {
                    "required_skills": ["Python", "AWS", "Docker"],
                    "preferred_skills": ["React", "TypeScript"],
                    "required_experience_years": 5
                },
                "compensation_range": "$120k-$180k",
                "status": "active"
            }
        }