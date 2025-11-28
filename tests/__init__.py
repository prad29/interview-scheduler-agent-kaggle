"""
Tests package for Intelligent Recruitment System

This package contains unit tests, integration tests, and test utilities
for all components of the recruitment system.

Test Structure:
- test_agents/: Tests for AI agents (resume parser, skills matcher, cultural fit, orchestrator)
- test_tools/: Tests for utility tools (PDF parser, DOCX parser, calendar, email)
- test_integration/: Integration tests for full workflows
- test_api/: Tests for API endpoints (if needed)
- test_models/: Tests for data models (if needed)

Running Tests:
    # Run all tests
    pytest tests/ -v
    
    # Run specific test file
    pytest tests/test_agents/test_resume_parser.py -v
    
    # Run with coverage
    pytest tests/ --cov=agents --cov=tools --cov-report=html
    
    # Run integration tests only
    pytest tests/ -m integration -v
    
    # Run with output
    pytest tests/ -v -s

Test Markers:
    @pytest.mark.asyncio - For async tests
    @pytest.mark.integration - For integration tests
    @pytest.mark.slow - For slow-running tests
    @pytest.mark.skip - Skip test
    @pytest.mark.skipif - Conditional skip
"""

import sys
import os
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test configuration
TEST_DATA_DIR = project_root / "data" / "test_data"
SAMPLE_RESUMES_DIR = project_root / "data" / "sample_resumes"
SAMPLE_DATA_DIR = project_root / "data" / "sample_data"

# Ensure test data directories exist
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Version info
__version__ = "1.0.0"
__author__ = "Intelligent Recruitment System Team"

# Test utilities and helpers

def setup_test_environment():
    """
    Setup test environment
    
    This function is called before running tests to ensure
    the test environment is properly configured.
    """
    # Set test environment variable
    os.environ['TESTING'] = 'true'
    
    # Disable debug mode for tests
    os.environ['DEBUG'] = 'false'
    
    # Use in-memory database for tests
    if 'DATABASE_URL' not in os.environ:
        os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    
    print("Test environment configured")


def teardown_test_environment():
    """
    Teardown test environment
    
    This function is called after running tests to clean up.
    """
    # Remove test environment variable
    if 'TESTING' in os.environ:
        del os.environ['TESTING']
    
    print("Test environment cleaned up")


# Common test fixtures and utilities

class TestConfig:
    """Test configuration constants"""
    
    # Timeouts
    DEFAULT_TIMEOUT = 30  # seconds
    LONG_TIMEOUT = 60  # seconds
    
    # Test data
    TEST_EMAIL = "test@example.com"
    TEST_PHONE = "+1-555-0000"
    TEST_NAME = "Test User"
    
    # Mock API responses
    MOCK_RESUME_PARSE_SUCCESS = True
    MOCK_SKILLS_MATCH_SUCCESS = True
    MOCK_CULTURAL_FIT_SUCCESS = True
    
    # Test thresholds
    MIN_PARSE_CONFIDENCE = 0.8
    MIN_SKILLS_MATCH = 0.7
    MIN_CULTURAL_FIT = 0.65


class MockAPIResponse:
    """Mock API response for testing without actual API calls"""
    
    @staticmethod
    def mock_resume_parser_response():
        """Mock response for resume parser"""
        return {
            "status": "success",
            "candidate_data": {
                "personal_info": {
                    "name": "John Doe",
                    "email": "john.doe@email.com",
                    "phone": "+1-555-0123"
                },
                "work_experience": [
                    {
                        "company": "Tech Corp",
                        "role": "Senior Engineer",
                        "start_date": "2020-01",
                        "end_date": "Present",
                        "responsibilities": ["Led team", "Built systems"],
                        "technologies": ["Python", "AWS"]
                    }
                ],
                "education": [
                    {
                        "institution": "MIT",
                        "degree": "BS",
                        "field_of_study": "Computer Science",
                        "graduation_date": "2018"
                    }
                ],
                "skills": ["Python", "AWS", "Docker", "Kubernetes"]
            },
            "confidence_scores": {
                "personal_info": 0.95,
                "work_experience": 0.90,
                "education": 0.92,
                "skills": 0.88
            }
        }
    
    @staticmethod
    def mock_skills_matcher_response():
        """Mock response for skills matcher"""
        return {
            "status": "success",
            "match_score": 0.85,
            "matched_skills": ["Python", "AWS", "Docker"],
            "missing_skills": ["Kubernetes"],
            "transferable_skills": [],
            "rationale": "Strong technical match with most required skills present."
        }
    
    @staticmethod
    def mock_cultural_fit_response():
        """Mock response for cultural fit analyzer"""
        return {
            "status": "success",
            "cultural_fit_score": 0.82,
            "dimensional_scores": {
                "collaboration": 0.85,
                "innovation": 0.80,
                "fast_paced": 0.88
            },
            "rationale": "Good cultural alignment with collaborative work style."
        }


class TestDataGenerator:
    """Generate test data for various scenarios"""
    
    @staticmethod
    def generate_sample_resume_text(
        name="John Doe",
        years_experience=5,
        skills=None
    ):
        """Generate sample resume text"""
        if skills is None:
            skills = ["Python", "AWS", "Docker"]
        
        return f"""
        {name}
        {name.lower().replace(' ', '.')}@email.com
        
        Professional Summary
        Software Engineer with {years_experience} years of experience
        
        Experience
        Tech Company - Engineer (2020-Present)
        - Developed applications
        - Technologies: {', '.join(skills)}
        
        Education
        University - BS Computer Science (2018)
        
        Skills
        {', '.join(skills)}
        """
    
    @staticmethod
    def generate_job_description(
        title="Software Engineer",
        required_skills=None,
        preferred_skills=None
    ):
        """Generate sample job description"""
        if required_skills is None:
            required_skills = ["Python", "AWS"]
        if preferred_skills is None:
            preferred_skills = ["Docker"]
        
        return {
            "title": title,
            "required_skills": required_skills,
            "preferred_skills": preferred_skills,
            "experience_level": "Mid-level",
            "responsibilities": [
                "Develop software",
                "Collaborate with team"
            ]
        }
    
    @staticmethod
    def generate_candidate_data(candidate_id="test_001"):
        """Generate complete candidate data"""
        return {
            "id": candidate_id,
            "personal_info": {
                "name": "Test Candidate",
                "email": f"candidate_{candidate_id}@email.com",
                "phone": "+1-555-0123"
            },
            "work_experience": [
                {
                    "company": "Test Company",
                    "role": "Engineer",
                    "technologies": ["Python", "AWS"]
                }
            ],
            "education": [
                {
                    "institution": "Test University",
                    "degree": "BS",
                    "field_of_study": "Computer Science"
                }
            ],
            "skills": ["Python", "AWS", "Docker"]
        }


# Test markers documentation
MARKERS = {
    'asyncio': 'Mark test as async',
    'integration': 'Mark test as integration test',
    'slow': 'Mark test as slow-running',
    'api': 'Mark test as requiring API access',
    'database': 'Mark test as requiring database',
    'file_system': 'Mark test as requiring file system access'
}

# Export commonly used items
__all__ = [
    'TestConfig',
    'MockAPIResponse',
    'TestDataGenerator',
    'setup_test_environment',
    'teardown_test_environment',
    'TEST_DATA_DIR',
    'SAMPLE_RESUMES_DIR',
    'SAMPLE_DATA_DIR',
    'MARKERS'
]


# Print test info when module is imported
if __name__ != "__main__":
    print(f"Tests package initialized (version {__version__})")