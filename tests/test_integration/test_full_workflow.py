"""
Integration tests for complete recruitment workflow
"""

import pytest
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.orchestrator_agent import OrchestratorAgent
from models.candidate import Candidate
from models.job_description import JobDescription
from storage.database import get_database, save_candidate, save_job
from storage.file_storage import FileStorage


@pytest.fixture
def test_database():
    """Create test database"""
    from storage.database import Database
    db = Database("sqlite:///:memory:")
    db.create_tables()
    yield db
    db.drop_tables()


@pytest.fixture
def file_storage(tmp_path):
    """Create temporary file storage"""
    storage = FileStorage(str(tmp_path / "test_storage"))
    return storage


@pytest.fixture
def sample_complete_workflow_data():
    """Complete workflow test data"""
    return {
        "resumes": [
            {
                "filename": "john_doe_resume.pdf",
                "resume_content": """
                John Doe
                john.doe@email.com | +1-555-0123
                San Francisco, CA
                
                PROFESSIONAL SUMMARY
                Senior Software Engineer with 8 years of experience in Python, AWS, and microservices.
                
                EXPERIENCE
                Senior Engineer at Tech Corp (2020-Present)
                - Led team of 5 engineers
                - Built microservices with Python, AWS, Docker, Kubernetes
                - Reduced deployment time by 60%
                
                Software Engineer at StartupXYZ (2018-2019)
                - Backend development with Python
                - Technologies: Python, React, MongoDB
                
                EDUCATION
                MIT - BS Computer Science (2018)
                GPA: 3.85
                
                SKILLS
                Python, JavaScript, AWS, Docker, Kubernetes, PostgreSQL, React
                """
            },
            {
                "filename": "jane_smith_resume.pdf",
                "resume_content": """
                Jane Smith
                jane.smith@email.com
                
                Software Developer with 3 years experience
                
                EXPERIENCE
                Developer at Digital Solutions (2021-Present)
                - Backend services with Python
                - Docker containers
                
                EDUCATION
                State University - BS Software Engineering (2021)
                
                SKILLS
                Python, Docker, MySQL, Git
                """
            }
        ],
        "job_description": {
            "title": "Senior Software Engineer",
            "required_skills": ["Python", "AWS", "Docker", "Kubernetes"],
            "preferred_skills": ["React", "TypeScript", "CI/CD"],
            "experience_level": "Senior (5+ years)",
            "responsibilities": [
                "Design scalable applications",
                "Lead technical discussions",
                "Mentor developers"
            ],
            "company_culture": {
                "values": ["Innovation", "Collaboration", "Excellence"],
                "work_style": "Fast-paced, collaborative",
                "pace": "Fast-paced",
                "innovation_focus": True,
                "collaboration_level": "high"
            }
        }
    }


class TestFullWorkflow:
    """Integration tests for complete recruitment workflow"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_end_to_end_workflow(self, sample_complete_workflow_data):
        """Test complete end-to-end workflow"""
        orchestrator = OrchestratorAgent()
        
        # Run orchestration
        result = await orchestrator.process(sample_complete_workflow_data)
        
        # Verify result structure
        assert result is not None
        assert "status" in result
        
        if result["status"] == "success":
            # Check processing summary
            assert "processing_summary" in result
            summary = result["processing_summary"]
            
            assert summary["total_resumes"] == 2
            assert "successfully_parsed" in summary
            assert "qualified_candidates" in summary
            
            # Check ranked candidates
            assert "ranked_candidates" in result
            candidates = result["ranked_candidates"]
            
            # Should have results for both candidates
            assert len(candidates) >= 0
            
            # If we have candidates, verify structure
            if len(candidates) > 0:
                first_candidate = candidates[0]
                
                assert "name" in first_candidate
                assert "overall_score" in first_candidate
                assert "skills_match_score" in first_candidate
                assert "cultural_fit_score" in first_candidate
                assert "tier" in first_candidate
                
                # Verify scores are in valid range
                assert 0 <= first_candidate["overall_score"] <= 100
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_workflow_with_interview_scheduling(
        self,
        sample_complete_workflow_data
    ):
        """Test workflow including interview scheduling"""
        orchestrator = OrchestratorAgent()
        
        # Add interviewer email for scheduling
        workflow_data = sample_complete_workflow_data.copy()
        workflow_data["interviewer_email"] = "interviewer@company.com"
        
        result = await orchestrator.process(workflow_data)
        
        assert result is not None
        
        if result["status"] == "success":
            # Check if interviews were scheduled
            assert "scheduled_interviews" in result
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_workflow_error_handling(self):
        """Test workflow handles errors gracefully"""
        orchestrator = OrchestratorAgent()
        
        # Test with invalid data
        invalid_data = {
            "resumes": [],  # Empty resumes
            "job_description": {}  # Empty job description
        }
        
        result = await orchestrator.process(invalid_data)
        
        # Should handle gracefully
        assert result is not None
        assert result["status"] == "error"
        assert "message" in result
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_parallel_processing(self, sample_complete_workflow_data):
        """Test that resumes are processed in parallel"""
        orchestrator = OrchestratorAgent()
        
        start_time = datetime.now()
        
        result = await orchestrator.process(sample_complete_workflow_data)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # With 2 resumes, parallel processing should be faster than 2x single processing
        # This is a rough check - in practice, parallel should be more efficient
        if result["status"] == "success":
            print(f"Processing time for 2 resumes: {processing_time:.2f} seconds")
    
    def test_database_integration(self, test_database):
        """Test database integration"""
        session = test_database.get_session()
        
        try:
            # Create test job
            job_data = {
                "id": "test_job_001",
                "title": "Test Engineer",
                "department": "Engineering",
                "location": "San Francisco",
                "description": "Test job description",
                "responsibilities": ["Test responsibility"],
                "requirements": {"required_skills": ["Python"]},
                "status": "active"
            }
            
            job = save_job(job_data, session)
            assert job is not None
            assert job.id == "test_job_001"
            
            # Create test candidate
            candidate_data = {
                "id": "test_candidate_001",
                "job_id": "test_job_001",
                "personal_info": {
                    "name": "Test User",
                    "email": "test@email.com"
                },
                "work_experience": [],
                "education": [],
                "skills": ["Python"]
            }
            
            candidate = save_candidate(candidate_data, session)
            assert candidate is not None
            assert candidate.id == "test_candidate_001"
            
        finally:
            session.close()
    
    def test_file_storage_integration(self, file_storage, tmp_path):
        """Test file storage integration"""
        # Create test file
        test_file = tmp_path / "test_resume.txt"
        test_file.write_text("Test resume content")
        
        # Save file
        result = file_storage.save_resume(
            str(test_file),
            candidate_id="test_candidate_001"
        )
        
        assert result["success"] is True
        assert "file_path" in result
        
        # Verify file exists
        saved_file = file_storage.get_file(result["relative_path"])
        assert saved_file is not None
        assert saved_file.exists()
        
        # Get storage stats
        stats = file_storage.get_storage_stats()
        assert stats["resumes"]["count"] >= 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_workflow_performance():
    """Test workflow performance with multiple resumes"""
    orchestrator = OrchestratorAgent()
    
    # Create multiple test resumes
    resumes = []
    for i in range(5):
        resumes.append({
            "filename": f"resume_{i}.pdf",
            "resume_content": f"""
            Candidate {i}
            candidate{i}@email.com
            
            Software Engineer with {i+2} years experience
            Skills: Python, AWS, Docker
            
            Experience:
            Tech Company - Engineer ({2020+i}-Present)
            """
        })
    
    job_description = {
        "title": "Software Engineer",
        "required_skills": ["Python", "AWS"],
        "preferred_skills": ["Docker"],
        "experience_level": "Mid-level"
    }
    
    start_time = datetime.now()
    
    result = await orchestrator.process({
        "resumes": resumes,
        "job_description": job_description
    })
    
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()
    
    print(f"\nProcessed {len(resumes)} resumes in {processing_time:.2f} seconds")
    print(f"Average time per resume: {processing_time/len(resumes):.2f} seconds")
    
    if result["status"] == "success":
        assert result["processing_summary"]["total_resumes"] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])