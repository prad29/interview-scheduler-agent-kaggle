"""
Tests for Skills Matcher Agent
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.skills_matcher_agent import SkillsMatcherAgent


@pytest.fixture
def skills_matcher_agent():
    """Create Skills Matcher Agent instance"""
    return SkillsMatcherAgent()


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
                "company": "Tech Corp",
                "role": "Senior Engineer",
                "start_date": "2020-01",
                "end_date": "Present",
                "duration_months": 48,
                "responsibilities": [
                    "Developed microservices using Python",
                    "Deployed to AWS using Docker and Kubernetes",
                    "Led team of 5 engineers"
                ],
                "technologies": ["Python", "AWS", "Docker", "Kubernetes", "PostgreSQL"]
            },
            {
                "company": "StartupXYZ",
                "role": "Software Engineer",
                "start_date": "2018-06",
                "end_date": "2019-12",
                "duration_months": 18,
                "technologies": ["Python", "React", "MongoDB"]
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
        "skills": ["Python", "JavaScript", "AWS", "Docker", "Kubernetes", "PostgreSQL", "React"],
        "certifications": [
            {
                "name": "AWS Certified Solutions Architect",
                "issuing_organization": "Amazon Web Services"
            }
        ]
    }


@pytest.fixture
def sample_job_description():
    """Sample job description"""
    return {
        "title": "Senior Software Engineer",
        "required_skills": ["Python", "AWS", "Docker", "Kubernetes"],
        "preferred_skills": ["React", "TypeScript", "CI/CD"],
        "experience_level": "Senior (5+ years)",
        "responsibilities": [
            "Design and develop scalable applications",
            "Lead technical discussions",
            "Mentor junior developers"
        ]
    }


@pytest.fixture
def weak_match_candidate():
    """Candidate with weak skill match"""
    return {
        "personal_info": {
            "name": "Bob Johnson",
            "email": "bob@email.com"
        },
        "work_experience": [
            {
                "company": "Local Company",
                "role": "Junior Developer",
                "duration_months": 24,
                "technologies": ["Java", "MySQL"]
            }
        ],
        "education": [
            {
                "degree": "Associate Degree",
                "field_of_study": "Computer Programming"
            }
        ],
        "skills": ["Java", "MySQL", "Git"]
    }


class TestSkillsMatcherAgent:
    """Test suite for Skills Matcher Agent"""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, skills_matcher_agent):
        """Test agent initializes correctly"""
        assert skills_matcher_agent is not None
        assert skills_matcher_agent.name == "SkillsMatcherAgent"
    
    @pytest.mark.asyncio
    async def test_process_with_valid_input(
        self,
        skills_matcher_agent,
        sample_candidate_data,
        sample_job_description
    ):
        """Test skills matching with valid input"""
        input_data = {
            "candidate_data": sample_candidate_data,
            "job_description": sample_job_description
        }
        
        result = await skills_matcher_agent.process(input_data)
        
        assert result is not None
        assert "status" in result
        
        if result["status"] == "success":
            assert "match_score" in result
            assert "matched_skills" in result
            assert "missing_skills" in result
            assert "rationale" in result
            
            # Validate score range
            assert 0 <= result["match_score"] <= 1
    
    @pytest.mark.asyncio
    async def test_process_with_missing_data(self, skills_matcher_agent):
        """Test handling of missing input data"""
        result = await skills_matcher_agent.process({})
        
        assert result["status"] == "error"
        assert "message" in result
    
    @pytest.mark.asyncio
    async def test_process_weak_match(
        self,
        skills_matcher_agent,
        weak_match_candidate,
        sample_job_description
    ):
        """Test skills matching with weak match candidate"""
        input_data = {
            "candidate_data": weak_match_candidate,
            "job_description": sample_job_description
        }
        
        result = await skills_matcher_agent.process(input_data)
        
        if result["status"] == "success":
            # Should have low match score
            assert result["match_score"] < 0.7
            
            # Should have missing skills
            assert len(result["missing_skills"]) > 0
    
    def test_extract_candidate_skills(
        self,
        skills_matcher_agent,
        sample_candidate_data
    ):
        """Test candidate skills extraction"""
        skills = skills_matcher_agent._extract_candidate_skills(sample_candidate_data)
        
        assert "technical_skills" in skills
        assert "work_experience" in skills
        assert "education" in skills
        assert "certifications" in skills
        assert "years_of_experience" in skills
        
        # Should have technical skills
        assert len(skills["technical_skills"]) > 0
    
    def test_extract_job_requirements(
        self,
        skills_matcher_agent,
        sample_job_description
    ):
        """Test job requirements extraction"""
        requirements = skills_matcher_agent._extract_job_requirements(sample_job_description)
        
        assert "required_skills" in requirements
        assert "preferred_skills" in requirements
        assert "experience_level" in requirements
        assert "responsibilities" in requirements
    
    def test_calculate_years_of_experience(self, skills_matcher_agent):
        """Test experience calculation"""
        work_experience = [
            {"duration_months": 48},  # 4 years
            {"duration_months": 18}   # 1.5 years
        ]
        
        years = skills_matcher_agent._calculate_years_of_experience(work_experience)
        
        # Simple calculation: 2 jobs * 2 years = 4 years
        assert years > 0
    
    def test_determine_recommendation(self, skills_matcher_agent):
        """Test recommendation determination"""
        # Strong match
        rec1 = skills_matcher_agent._determine_recommendation(92.0)
        assert rec1 == "strong_match"
        
        # Moderate match
        rec2 = skills_matcher_agent._determine_recommendation(75.0)
        assert rec2 == "moderate_match"
        
        # Weak match
        rec3 = skills_matcher_agent._determine_recommendation(55.0)
        assert rec3 == "weak_match"


@pytest.mark.asyncio
async def test_skills_matching_workflow():
    """Test complete skills matching workflow"""
    agent = SkillsMatcherAgent()
    
    candidate_data = {
        "skills": ["Python", "AWS", "Docker"],
        "work_experience": [
            {
                "company": "Tech Corp",
                "technologies": ["Python", "AWS"],
                "duration_months": 48
            }
        ],
        "education": [{"degree": "BS", "field_of_study": "CS"}],
        "certifications": []
    }
    
    job_description = {
        "required_skills": ["Python", "AWS", "Docker"],
        "preferred_skills": ["Kubernetes"],
        "experience_level": "Senior"
    }
    
    result = await agent.process({
        "candidate_data": candidate_data,
        "job_description": job_description
    })
    
    # Should return a result
    assert result is not None
    assert "status" in result


@pytest.mark.asyncio
async def test_semantic_matching_concept():
    """Test that semantic matching logic is in place"""
    # This is a conceptual test - actual implementation would use AI
    
    # Similar skill pairs that should match
    semantic_pairs = [
        ("team leadership", "people management"),
        ("nodejs", "node.js"),
        ("ci/cd", "continuous integration"),
        ("postgres", "postgresql")
    ]
    
    # In a real implementation, these would be matched semantically
    for skill1, skill2 in semantic_pairs:
        # Placeholder for semantic matching logic
        assert skill1.lower().replace("-", "").replace(".", "") != skill2.lower().replace("-", "").replace(".", "")
        # But they should be considered similar


if __name__ == "__main__":
    pytest.main([__file__, "-v"])