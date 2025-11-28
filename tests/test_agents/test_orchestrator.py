"""
Tests for Orchestrator Agent
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.orchestrator_agent import OrchestratorAgent


@pytest.fixture
def orchestrator_agent():
    """Create Orchestrator Agent instance"""
    return OrchestratorAgent()


@pytest.fixture
def sample_resumes():
    """Sample resume data for testing"""
    return [
        {
            "filename": "resume1.pdf",
            "resume_content": """
            John Doe
            john.doe@email.com
            
            Senior Software Engineer with 8 years of experience in Python, AWS, and Docker.
            
            Experience:
            Tech Corp - Senior Engineer (2020-Present)
            - Led team of 5 engineers
            - Built microservices architecture
            - Technologies: Python, AWS, Docker, Kubernetes
            
            Education:
            MIT - BS Computer Science (2016)
            """
        },
        {
            "filename": "resume2.pdf",
            "resume_content": """
            Jane Smith
            jane.smith@email.com
            
            Software Developer with 3 years of experience.
            
            Experience:
            StartupXYZ - Developer (2021-Present)
            - Backend development
            - Technologies: Python, Docker
            
            Education:
            State University - BS Software Engineering (2021)
            """
        }
    ]


@pytest.fixture
def sample_job_description():
    """Sample job description"""
    return {
        "title": "Senior Software Engineer",
        "required_skills": ["Python", "AWS", "Docker", "Kubernetes"],
        "preferred_skills": ["React", "TypeScript"],
        "experience_level": "Senior (5+ years)",
        "responsibilities": [
            "Design scalable applications",
            "Lead technical discussions",
            "Mentor junior developers"
        ]
    }


class TestOrchestratorAgent:
    """Test suite for Orchestrator Agent"""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, orchestrator_agent):
        """Test orchestrator initializes correctly"""
        assert orchestrator_agent is not None
        assert orchestrator_agent.name == "OrchestratorAgent"
        assert orchestrator_agent.resume_parser is not None
        assert orchestrator_agent.skills_matcher is not None
        assert orchestrator_agent.cultural_fit is not None
        assert orchestrator_agent.interview_scheduler is not None
    
    @pytest.mark.asyncio
    async def test_process_with_empty_resumes(
        self,
        orchestrator_agent,
        sample_job_description
    ):
        """Test handling of empty resume list"""
        result = await orchestrator_agent.process({
            "resumes": [],
            "job_description": sample_job_description
        })
        
        assert result["status"] == "error"
        assert "message" in result
        assert "No resumes provided" in result["message"]
    
    @pytest.mark.asyncio
    async def test_process_with_missing_job_description(
        self,
        orchestrator_agent,
        sample_resumes
    ):
        """Test handling of missing job description"""
        result = await orchestrator_agent.process({
            "resumes": sample_resumes,
            "job_description": {}
        })
        
        assert result["status"] == "error"
        assert "No job description provided" in result["message"]
    
    @pytest.mark.asyncio
    async def test_parse_single_resume(self, orchestrator_agent):
        """Test parsing a single resume"""
        resume = {
            "resume_content": "John Doe\njohn@email.com\nSoftware Engineer"
        }
        
        result = await orchestrator_agent._parse_single_resume(resume, 0)
        
        assert result is not None
        assert "status" in result
    
    @pytest.mark.asyncio
    async def test_rank_candidates(self, orchestrator_agent):
        """Test candidate ranking logic"""
        candidates = [
            {
                "id": "candidate_1",
                "candidate_data": {
                    "personal_info": {"name": "John Doe", "email": "john@email.com"},
                    "work_experience": [{"duration_months": 96}]
                },
                "skills_evaluation": {
                    "match_score": 0.90,
                    "matched_skills": ["Python", "AWS"],
                    "missing_skills": [],
                    "rationale": "Strong match"
                },
                "cultural_evaluation": {
                    "cultural_fit_score": 0.85,
                    "dimensional_scores": {},
                    "rationale": "Good fit"
                }
            },
            {
                "id": "candidate_2",
                "candidate_data": {
                    "personal_info": {"name": "Jane Smith", "email": "jane@email.com"},
                    "work_experience": [{"duration_months": 36}]
                },
                "skills_evaluation": {
                    "match_score": 0.75,
                    "matched_skills": ["Python"],
                    "missing_skills": ["AWS"],
                    "rationale": "Moderate match"
                },
                "cultural_evaluation": {
                    "cultural_fit_score": 0.70,
                    "dimensional_scores": {},
                    "rationale": "Reasonable fit"
                }
            }
        ]
        
        ranked = orchestrator_agent._rank_candidates(candidates)
        
        assert len(ranked) == 2
        # First candidate should be ranked higher
        assert ranked[0]["overall_score"] > ranked[1]["overall_score"]
        assert ranked[0]["tier"] in ["strong_match", "moderate_match", "weak_match"]
    
    def test_determine_tier(self, orchestrator_agent):
        """Test tier determination logic"""
        # Strong match
        tier1 = orchestrator_agent._determine_tier(0.87)
        assert tier1 == "strong_match"
        
        # Moderate match
        tier2 = orchestrator_agent._determine_tier(0.75)
        assert tier2 == "moderate_match"
        
        # Weak match
        tier3 = orchestrator_agent._determine_tier(0.60)
        assert tier3 == "weak_match"
    
    def test_filter_qualified_candidates(self, orchestrator_agent):
        """Test filtering of qualified candidates"""
        ranked_candidates = [
            {
                "id": "1",
                "skills_match_score": 85.0,
                "cultural_fit_score": 75.0,
                "tier": "strong_match"
            },
            {
                "id": "2",
                "skills_match_score": 72.0,
                "cultural_fit_score": 68.0,
                "tier": "moderate_match"
            },
            {
                "id": "3",
                "skills_match_score": 65.0,
                "cultural_fit_score": 60.0,
                "tier": "weak_match"
            }
        ]
        
        qualified = orchestrator_agent._filter_qualified_candidates(ranked_candidates)
        
        # Should only include candidates meeting thresholds
        assert len(qualified) <= len(ranked_candidates)
        
        for candidate in qualified:
            assert candidate["skills_match_score"] >= 70
            assert candidate["cultural_fit_score"] >= 65
    
    def test_get_years_of_experience(self, orchestrator_agent):
        """Test experience calculation"""
        candidate_data = {
            "work_experience": [
                {"duration_months": 48},  # 4 years
                {"duration_months": 24}   # 2 years
            ]
        }
        
        years = orchestrator_agent._get_years_of_experience(candidate_data)
        
        # Simple calculation: number of jobs * 2
        assert years > 0


@pytest.mark.asyncio
async def test_orchestration_workflow():
    """Test complete orchestration workflow (integration-style test)"""
    orchestrator = OrchestratorAgent()
    
    # Minimal test data
    resumes = [
        {
            "resume_content": "John Doe\njohn@email.com\nPython developer with 5 years experience"
        }
    ]
    
    job_description = {
        "title": "Software Engineer",
        "required_skills": ["Python"],
        "preferred_skills": [],
        "experience_level": "Mid-level"
    }
    
    # This would require actual API access, so we expect it to either:
    # 1. Succeed if API key is configured
    # 2. Fail gracefully if not configured
    try:
        result = await orchestrator.process({
            "resumes": resumes,
            "job_description": job_description,
            "company_culture": {},
            "interviewer_email": None
        })
        
        assert result is not None
        assert "status" in result
        
    except Exception as e:
        # Expected if API key not configured
        assert "API" in str(e) or "key" in str(e).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])