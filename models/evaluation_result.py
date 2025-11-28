from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class RecommendationType(str, Enum):
    """Candidate recommendation type"""
    STRONG_MATCH = "strong_match"
    MODERATE_MATCH = "moderate_match"
    WEAK_MATCH = "weak_match"
    REJECTED = "rejected"


class DimensionalScore(BaseModel):
    """Score for a specific cultural dimension"""
    dimension_name: str = Field(..., description="Name of the cultural dimension")
    score: float = Field(..., ge=0.0, le=1.0, description="Score for this dimension (0.0-1.0)")
    description: Optional[str] = Field(None, description="Description of what this dimension measures")
    evidence: List[str] = Field(
        default_factory=list,
        description="Evidence from resume supporting this score"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "dimension_name": "Collaboration vs Independence",
                "score": 0.85,
                "description": "Measures preference for team collaboration vs autonomous work",
                "evidence": [
                    "Led cross-functional team of 8 members",
                    "Collaborated with product and design teams"
                ]
            }
        }


class SkillsEvaluation(BaseModel):
    """Skills matching evaluation result"""
    overall_match_percentage: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Overall skills match percentage"
    )
    
    # Detailed breakdown
    required_skills_match: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Match percentage for required skills"
    )
    preferred_skills_match: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Match percentage for preferred skills"
    )
    
    # Matched and missing skills
    matched_skills: List[str] = Field(
        default_factory=list,
        description="Skills that matched job requirements"
    )
    missing_skills: List[str] = Field(
        default_factory=list,
        description="Required skills that candidate is missing"
    )
    transferable_skills: List[str] = Field(
        default_factory=list,
        description="Skills that could transfer to required skills"
    )
    bonus_skills: List[str] = Field(
        default_factory=list,
        description="Additional skills not in requirements"
    )
    
    # Detailed analysis
    skills_breakdown: Dict[str, Any] = Field(
        default_factory=dict,
        description="Detailed breakdown by skill category"
    )
    experience_match: Optional[str] = Field(
        None,
        description="How candidate's experience matches requirements"
    )
    
    # Rationale
    rationale: str = Field(
        ...,
        description="Detailed explanation of skills matching"
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Candidate's key strengths"
    )
    gaps: List[str] = Field(
        default_factory=list,
        description="Identified skill gaps"
    )
    
    # Confidence
    confidence_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Confidence in the evaluation (0.0-1.0)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "overall_match_percentage": 87.5,
                "required_skills_match": 90.0,
                "preferred_skills_match": 75.0,
                "matched_skills": ["Python", "AWS", "Docker", "Kubernetes"],
                "missing_skills": ["React"],
                "transferable_skills": ["Angular", "Vue.js"],
                "bonus_skills": ["Machine Learning", "TensorFlow"],
                "rationale": "Candidate demonstrates strong technical skills...",
                "strengths": ["Deep cloud infrastructure experience", "Leadership skills"],
                "gaps": ["Limited frontend experience"],
                "confidence_score": 0.92
            }
        }


class CulturalFitEvaluation(BaseModel):
    """Cultural fit evaluation result"""
    overall_cultural_fit_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Overall cultural fit score (0-100)"
    )
    
    # Dimensional analysis
    dimensional_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Scores for each cultural dimension"
    )
    detailed_dimensions: List[DimensionalScore] = Field(
        default_factory=list,
        description="Detailed analysis of each dimension"
    )
    
    # Analysis
    rationale: str = Field(
        ...,
        description="Detailed explanation of cultural fit assessment"
    )
    evidence: List[str] = Field(
        default_factory=list,
        description="Evidence from resume supporting the assessment"
    )
    
    # Alignment and concerns
    alignment_areas: List[str] = Field(
        default_factory=list,
        description="Areas of strong cultural alignment"
    )
    potential_concerns: List[str] = Field(
        default_factory=list,
        description="Potential cultural misalignments"
    )
    
    # Interview recommendations
    interview_discussion_points: List[str] = Field(
        default_factory=list,
        description="Points to explore during interview"
    )
    
    # Confidence
    confidence_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Confidence in the evaluation (0.0-1.0)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "overall_cultural_fit_score": 82.0,
                "dimensional_scores": {
                    "Collaboration": 0.85,
                    "Innovation": 0.80,
                    "Fast-paced": 0.88
                },
                "rationale": "Candidate shows strong alignment with company culture...",
                "evidence": [
                    "Worked in fast-paced startup environments",
                    "Led collaborative cross-functional projects"
                ],
                "alignment_areas": ["Team collaboration", "Innovation focus"],
                "potential_concerns": ["Adaptation to hierarchical structure"],
                "interview_discussion_points": [
                    "Experience with different organizational structures"
                ],
                "confidence_score": 0.85
            }
        }


class EvaluationResult(BaseModel):
    """Complete evaluation result for a candidate"""
    # Identifiers
    candidate_id: str = Field(..., description="Candidate identifier")
    job_id: str = Field(..., description="Job identifier")
    evaluation_id: Optional[str] = Field(None, description="Unique evaluation identifier")
    
    # Overall scores
    overall_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Weighted overall score (0-100)"
    )
    
    # Component evaluations
    skills_evaluation: SkillsEvaluation = Field(
        ...,
        description="Skills matching evaluation"
    )
    cultural_evaluation: CulturalFitEvaluation = Field(
        ...,
        description="Cultural fit evaluation"
    )
    
    # Additional scores
    experience_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Experience level match score"
    )
    education_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Education match score"
    )
    
    # Recommendation
    recommendation: RecommendationType = Field(
        ...,
        description="Overall recommendation"
    )
    tier: str = Field(
        ...,
        description="Candidate tier (strong_match, moderate_match, weak_match)"
    )
    
    # Summary
    executive_summary: Optional[str] = Field(
        None,
        description="Executive summary of the evaluation"
    )
    key_highlights: List[str] = Field(
        default_factory=list,
        description="Key highlights about the candidate"
    )
    concerns: List[str] = Field(
        default_factory=list,
        description="Key concerns about the candidate"
    )
    
    # Next steps
    recommended_next_steps: List[str] = Field(
        default_factory=list,
        description="Recommended next steps (e.g., schedule interview)"
    )
    interview_focus_areas: List[str] = Field(
        default_factory=list,
        description="Areas to focus on during interview"
    )
    
    # Metadata
    evaluated_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when evaluation was performed"
    )
    evaluated_by: Optional[str] = Field(
        None,
        description="Agent or user who performed evaluation"
    )
    processing_time_seconds: Optional[float] = Field(
        None,
        ge=0.0,
        description="Time taken to perform evaluation"
    )
    
    # Weights used in calculation
    weights: Optional[Dict[str, float]] = Field(
        None,
        description="Weights used in overall score calculation"
    )
    
    @validator('recommendation')
    def validate_recommendation_matches_tier(cls, v, values):
        """Ensure recommendation matches tier"""
        if 'tier' in values:
            tier = values['tier']
            if tier == 'strong_match' and v not in [RecommendationType.STRONG_MATCH]:
                raise ValueError('Tier and recommendation must align')
        return v
    
    def to_summary(self) -> Dict[str, Any]:
        """Generate a summary of the evaluation"""
        return {
            'candidate_id': self.candidate_id,
            'job_id': self.job_id,
            'overall_score': round(self.overall_score, 2),
            'skills_match': round(self.skills_evaluation.overall_match_percentage, 2),
            'cultural_fit': round(self.cultural_evaluation.overall_cultural_fit_score, 2),
            'recommendation': self.recommendation.value,
            'tier': self.tier,
            'key_highlights': self.key_highlights[:3],
            'evaluated_at': self.evaluated_at.isoformat()
        }
    
    def meets_threshold(self, skills_threshold: float = 70.0, cultural_threshold: float = 65.0) -> bool:
        """Check if candidate meets minimum thresholds"""
        return (
            self.skills_evaluation.overall_match_percentage >= skills_threshold and
            self.cultural_evaluation.overall_cultural_fit_score >= cultural_threshold
        )
    
    class Config:
        json_schema_extra = {
            "example": {
                "candidate_id": "candidate_123",
                "job_id": "job_001",
                "overall_score": 87.5,
                "skills_evaluation": {
                    "overall_match_percentage": 90.0,
                    "matched_skills": ["Python", "AWS", "Docker"],
                    "missing_skills": ["React"],
                    "rationale": "Strong technical match..."
                },
                "cultural_evaluation": {
                    "overall_cultural_fit_score": 85.0,
                    "rationale": "Good cultural alignment..."
                },
                "recommendation": "strong_match",
                "tier": "strong_match",
                "key_highlights": [
                    "8 years of relevant experience",
                    "Strong cloud infrastructure skills"
                ]
            }
        }