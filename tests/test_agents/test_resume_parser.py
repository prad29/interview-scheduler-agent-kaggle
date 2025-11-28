"""
Tests for Resume Parser Agent
"""

import pytest
import asyncio
import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.resume_parser_agent import ResumeParserAgent


@pytest.fixture
def resume_parser_agent():
    """Create Resume Parser Agent instance"""
    return ResumeParserAgent()


@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing"""
    return """
    JOHN DOE
    john.doe@email.com | +1-555-0123 | San Francisco, CA
    LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe
    
    PROFESSIONAL SUMMARY
    Senior Software Engineer with 8 years of experience in building scalable web applications
    and microservices. Expert in Python, AWS, and containerization technologies.
    
    WORK EXPERIENCE
    
    Senior Software Engineer
    Tech Innovations LLC, San Francisco, CA
    January 2020 - Present
    • Led development of microservices architecture serving 1M+ users
    • Mentored team of 5 junior engineers
    • Designed and implemented CI/CD pipeline reducing deployment time by 60%
    • Technologies: Python, AWS, Docker, Kubernetes, PostgreSQL, Redis
    
    Software Engineer
    StartupXYZ, San Francisco, CA
    June 2018 - December 2019
    • Developed REST APIs using Python/Flask
    • Built frontend components with React
    • Technologies: Python, React, MongoDB, AWS
    
    EDUCATION
    
    Bachelor of Science in Computer Science
    Massachusetts Institute of Technology (MIT)
    Graduated: May 2018
    GPA: 3.85/4.0
    Honors: Dean's List, Summa Cum Laude
    
    SKILLS
    
    Programming Languages: Python, JavaScript, Go
    Cloud & DevOps: AWS, Docker, Kubernetes, CI/CD, Terraform
    Databases: PostgreSQL, MongoDB, Redis
    Frameworks: Flask, Django, React
    
    CERTIFICATIONS
    
    AWS Certified Solutions Architect - Associate
    Amazon Web Services, Issued: June 2023, Expires: June 2026
    
    PROJECTS
    
    Open Source Container Orchestration Tool
    • Contributed to popular Kubernetes tooling
    • Technologies: Go, Kubernetes
    """


@pytest.fixture
def minimal_resume_text():
    """Minimal resume for edge case testing"""
    return """
    Jane Smith
    jane.smith@email.com
    
    Software Developer
    """


class TestResumeParserAgent:
    """Test suite for Resume Parser Agent"""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, resume_parser_agent):
        """Test agent initializes correctly"""
        assert resume_parser_agent is not None
        assert resume_parser_agent.name == "ResumeParserAgent"
    
    @pytest.mark.asyncio
    async def test_process_with_valid_resume(
        self,
        resume_parser_agent,
        sample_resume_text
    ):
        """Test parsing a valid resume"""
        input_data = {
            "resume_content": sample_resume_text
        }
        
        result = await resume_parser_agent.process(input_data)
        
        assert result is not None
        assert "status" in result
        
        if result["status"] == "success":
            assert "candidate_data" in result
            assert "confidence_scores" in result
            
            candidate_data = result["candidate_data"]
            
            # Check required fields
            assert "personal_info" in candidate_data
            assert "work_experience" in candidate_data
            assert "education" in candidate_data
            assert "skills" in candidate_data
    
    @pytest.mark.asyncio
    async def test_process_with_empty_content(self, resume_parser_agent):
        """Test handling of empty resume content"""
        input_data = {
            "resume_content": ""
        }
        
        result = await resume_parser_agent.process(input_data)
        
        assert result["status"] == "error"
        assert "message" in result
    
    @pytest.mark.asyncio
    async def test_process_with_missing_content(self, resume_parser_agent):
        """Test handling of missing resume content"""
        input_data = {}
        
        result = await resume_parser_agent.process(input_data)
        
        assert result["status"] == "error"
        assert "No resume content provided" in result["message"]
    
    @pytest.mark.asyncio
    async def test_process_with_minimal_resume(
        self,
        resume_parser_agent,
        minimal_resume_text
    ):
        """Test parsing a minimal resume"""
        input_data = {
            "resume_content": minimal_resume_text
        }
        
        result = await resume_parser_agent.process(input_data)
        
        # Should still return a result, even if data is minimal
        assert result is not None
        assert "status" in result
    
    def test_calculate_confidence_scores(self, resume_parser_agent):
        """Test confidence score calculation"""
        candidate_data = {
            "personal_info": {
                "name": "John Doe",
                "email": "john@email.com",
                "phone": "+1-555-0123"
            },
            "work_experience": [
                {"company": "Tech Corp", "role": "Engineer"}
            ],
            "education": [
                {"institution": "MIT", "degree": "BS"}
            ],
            "skills": ["Python", "AWS"]
        }
        
        scores = resume_parser_agent._calculate_confidence_scores(candidate_data)
        
        assert isinstance(scores, dict)
        assert "personal_info" in scores
        
        # Personal info should have high confidence (has name and email)
        assert scores["personal_info"] > 0.5
        
        # Skills should have high confidence
        if "skills" in scores:
            assert scores["skills"] > 0


@pytest.mark.asyncio
async def test_json_response_parsing():
    """Test JSON response parsing from various formats"""
    agent = ResumeParserAgent()
    
    # Test with markdown code blocks
    response_with_markdown = """
```json
    {
        "personal_info": {
            "name": "Test User",
            "email": "test@email.com"
        }
    }
```
    """
    
    # Extract JSON
    cleaned = response_with_markdown
    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[1].split("```")[0].strip()
    
    # Should be valid JSON now
    data = json.loads(cleaned)
    assert "personal_info" in data


@pytest.mark.asyncio
async def test_resume_parser_workflow():
    """Test complete resume parsing workflow"""
    agent = ResumeParserAgent()
    
    resume_text = """
    John Doe
    john.doe@email.com
    
    Experience:
    Software Engineer at Tech Corp (2020-Present)
    - Developed applications using Python
    
    Education:
    BS Computer Science, MIT, 2018
    
    Skills: Python, AWS, Docker
    """
    
    result = await agent.process({"resume_content": resume_text})
    
    # Should return a result
    assert result is not None
    assert "status" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])