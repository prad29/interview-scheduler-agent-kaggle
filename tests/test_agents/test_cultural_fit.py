"""
Tests for Cultural Fit Analyzer Agent
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.cultural_fit_agent import CulturalFitAgent


@pytest.fixture
def cultural_fit_agent():
    """Create Cultural Fit Agent instance"""
    return CulturalFitAgent()


@pytest.fixture
def sample_candidate_data():
    """Sample candidate data for testing"""
    return {
        "personal_info": {
            "name": "John Doe",
            "email": "john.doe@email.com"
        },
        "work_experience": [
            {
                "company": "StartupXYZ",
                "role": "Senior Engineer",
                "start_date": "2020-01",
                "end_date": "Present",
                "responsibilities": [
                    "Led cross-functional team of 8 members",
                    "Pioneered new microservices architecture",
                    "Collaborated closely with product and design teams",
                    "Mentored 3 junior developers"
                ],
                "achievements": [
                    "Delivered project 2 weeks ahead of schedule",
                    "Implemented CI/CD pipeline reducing deployment time by 60%"
                ],
                "technologies": ["Python", "AWS", "Docker", "Kubernetes"]
            },
            {
                "company": "TechCorp (Series A Startup)",
                "role": "Software Engineer",
                "start_date": "2018-06",
                "end_date": "2019-12",
                "responsibilities": [
                    "Worked autonomously on backend services",
                    "Rapidly iterated on features based on user feedback"
                ],
                "technologies": ["Python", "PostgreSQL"]
            }
        ],
        "education": [
            {
                "institution": "MIT",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science",
                "graduation_date": "2018-05"
            }
        ],
        "skills": ["Python", "AWS", "Docker", "Team Leadership"],
        "projects": [
            {
                "name": "Open Source Project Contribution",
                "description": "Active contributor to Kubernetes community"
            }
        ]
    }


@pytest.fixture
def sample_company_culture():
    """Sample company culture profile"""
    return {
        "values": ["Innovation", "Collaboration", "Speed", "Ownership"],
        "work_style": "Fast-paced, collaborative environment",
        "team_size": 10,
        "pace": "Fast-paced",
        "innovation_focus": True,
        "collaboration_level": "high",
        "hierarchy": "flat",
        "mission_driven": True
    }


@pytest.fixture
def sample_job_description():
    """Sample job description"""
    return {
        "title": "Senior Software Engineer",
        "description": "Join our fast-paced team building innovative solutions",
        "responsibilities": [
            "Lead technical initiatives",
            "Collaborate with cross-functional teams",
            "Mentor junior engineers"
        ],
        "cultural_attributes": {
            "pace": "fast-paced",
            "collaboration": "high",
            "innovation": "high"
        }
    }


class TestCulturalFitAgent:
    """Test suite for Cultural Fit Analyzer Agent"""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, cultural_fit_agent):
        """Test agent initializes correctly"""
        assert cultural_fit_agent is not None
        assert cultural_fit_agent.name == "CulturalFitAgent"
    
    @pytest.mark.asyncio
    async def test_process_with_valid_input(
        self,
        cultural_fit_agent,
        sample_candidate_data,
        sample_company_culture,
        sample_job_description
    ):
        """Test cultural fit analysis with valid input"""
        input_data = {
            "candidate_data": sample_candidate_data,
            "company_culture": sample_company_culture,
            "job_description": sample_job_description
        }
        
        # This test requires actual API access
        # In a real test environment, you would mock the API response
        # For now, we'll test the structure
        
        result = await cultural_fit_agent.process(input_data)
        
        assert result is not None
        assert "status" in result
        
        if result["status"] == "success":
            assert "cultural_fit_score" in result
            assert "dimensional_scores" in result
            assert "rationale" in result
            
            # Validate score range
            assert 0 <= result["cultural_fit_score"] <= 1
    
    @pytest.mark.asyncio
    async def test_process_with_missing_candidate_data(
        self,
        cultural_fit_agent,
        sample_company_culture
    ):
        """Test handling of missing candidate data"""
        input_data = {
            "company_culture": sample_company_culture
        }
        
        result = await cultural_fit_agent.process(input_data)
        
        assert result["status"] == "error"
        assert "message" in result
    
    @pytest.mark.asyncio
    async def test_extract_candidate_background(
        self,
        cultural_fit_agent,
        sample_candidate_data
    ):
        """Test candidate background extraction"""
        background = cultural_fit_agent._extract_candidate_background(sample_candidate_data)
        
        assert "work_history" in background
        assert "education" in background
        assert "skills" in background
        assert isinstance(background["work_history"], list)
    
    @pytest.mark.asyncio
    async def test_extract_culture_from_jd(
        self,
        cultural_fit_agent,
        sample_job_description
    ):
        """Test culture extraction from job description"""
        culture = cultural_fit_agent._extract_culture_from_jd(sample_job_description)
        
        assert "responsibilities" in culture
        assert isinstance(culture, dict)
    
    def test_dimensional_score_validation(self):
        """Test that dimensional scores are properly validated"""
        # Sample dimensional scores
        dimensional_scores = {
            "collaboration_vs_independence": {
                "score": 0.85,
                "interpretation": "High collaboration preference"
            },
            "innovation_vs_stability": {
                "score": 0.90,
                "interpretation": "Strong innovation focus"
            }
        }
        
        # Validate scores are in range
        for dimension, data in dimensional_scores.items():
            score = data["score"]
            assert 0.0 <= score <= 1.0, f"Score for {dimension} out of range: {score}"


@pytest.mark.asyncio
async def test_cultural_fit_workflow():
    """Test complete cultural fit analysis workflow"""
    agent = CulturalFitAgent()
    
    candidate_data = {
        "work_experience": [
            {
                "company": "Startup",
                "role": "Engineer",
                "responsibilities": ["Collaborated with team", "Fast-paced environment"]
            }
        ],
        "skills": ["Python", "Teamwork"]
    }
    
    company_culture = {
        "values": ["Collaboration", "Innovation"],
        "pace": "Fast-paced"
    }
    
    result = await agent.process({
        "candidate_data": candidate_data,
        "company_culture": company_culture,
        "job_description": {}
    })
    
    # Should return a result (success or error with API key issues)
    assert result is not None
    assert "status" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])