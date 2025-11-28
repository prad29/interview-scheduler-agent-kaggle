#!/usr/bin/env python3
"""
Seed database with sample data for testing and development

This script creates sample:
- Job descriptions
- Candidate profiles
- Evaluation results
- Interview slots
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.candidate import Candidate, PersonalInfo, WorkExperience, Education
from models.job_description import JobDescription, JobRequirements, CompanyCulture, ExperienceLevel, EmploymentType, WorkLocation
from models.evaluation_result import EvaluationResult, SkillsEvaluation, CulturalFitEvaluation, RecommendationType
from models.interview_slot import InterviewSlot, InterviewStatus, InterviewType, MeetingPlatform, Attendee

def create_sample_jobs():
    """Create sample job descriptions"""
    
    jobs = []
    
    # Job 1: Senior Software Engineer
    job1 = JobDescription(
        id="job_001",
        title="Senior Software Engineer",
        department="Engineering",
        location="San Francisco, CA",
        work_location_type=WorkLocation.HYBRID,
        employment_type=EmploymentType.FULL_TIME,
        experience_level=ExperienceLevel.SENIOR,
        description="We are looking for a Senior Software Engineer to join our platform team. You will work on building scalable microservices and leading technical initiatives.",
        responsibilities=[
            "Design and develop scalable applications using modern technologies",
            "Lead technical discussions and architecture decisions",
            "Mentor junior developers and conduct code reviews",
            "Collaborate with product and design teams",
            "Contribute to engineering best practices and standards"
        ],
        requirements=JobRequirements(
            required_skills=["Python", "AWS", "Docker", "Kubernetes", "Microservices"],
            preferred_skills=["React", "TypeScript", "CI/CD", "GraphQL", "PostgreSQL"],
            required_experience_years=5,
            required_education="Bachelor's degree in Computer Science or related field",
            preferred_certifications=["AWS Certified Solutions Architect"],
            language_requirements=[{"language": "English", "level": "Fluent"}]
        ),
        salary_min=120000,
        salary_max=180000,
        salary_currency="USD",
        compensation_range="$120k-$180k",
        benefits=[
            "Competitive salary and equity",
            "Comprehensive health insurance",
            "401(k) matching",
            "Unlimited PTO",
            "Remote work flexibility",
            "Professional development budget"
        ],
        company_name="TechCorp Inc.",
        company_description="Leading technology company building innovative solutions",
        company_culture=CompanyCulture(
            values=["Innovation", "Collaboration", "Integrity", "Customer Focus"],
            work_style="Collaborative with autonomy",
            team_size=12,
            pace="Fast-paced",
            innovation_focus=True,
            collaboration_level="high",
            hierarchy="flat",
            mission_driven=True
        ),
        team_description="Platform engineering team responsible for core infrastructure",
        growth_opportunities=["Tech lead positions", "Architecture roles", "Management track"],
        reporting_to="Engineering Manager",
        hiring_manager="hiring.manager@techcorp.com",
        status="active"
    )
    jobs.append(job1)
    
    # Job 2: Product Manager
    job2 = JobDescription(
        id="job_002",
        title="Senior Product Manager",
        department="Product",
        location="Remote",
        work_location_type=WorkLocation.REMOTE,
        employment_type=EmploymentType.FULL_TIME,
        experience_level=ExperienceLevel.SENIOR,
        description="We're seeking an experienced Product Manager to drive product strategy and execution.",
        responsibilities=[
            "Define product vision and roadmap",
            "Gather and prioritize product requirements",
            "Work closely with engineering and design",
            "Analyze metrics and user feedback",
            "Lead product launches"
        ],
        requirements=JobRequirements(
            required_skills=["Product Management", "Roadmap Planning", "Stakeholder Management", "Data Analysis"],
            preferred_skills=["B2B SaaS", "Agile", "SQL", "A/B Testing"],
            required_experience_years=5,
            required_education="Bachelor's degree",
            language_requirements=[{"language": "English", "level": "Fluent"}]
        ),
        compensation_range="$130k-$170k",
        company_name="TechCorp Inc.",
        status="active"
    )
    jobs.append(job2)
    
    # Job 3: Data Scientist
    job3 = JobDescription(
        id="job_003",
        title="Data Scientist",
        department="Data Science",
        location="New York, NY",
        work_location_type=WorkLocation.HYBRID,
        employment_type=EmploymentType.FULL_TIME,
        experience_level=ExperienceLevel.MID,
        description="Join our data science team to build ML models and drive data-driven decisions.",
        responsibilities=[
            "Develop and deploy machine learning models",
            "Analyze large datasets to extract insights",
            "Collaborate with engineering to productionize models",
            "Present findings to stakeholders"
        ],
        requirements=JobRequirements(
            required_skills=["Python", "Machine Learning", "SQL", "Statistics"],
            preferred_skills=["TensorFlow", "PyTorch", "Spark", "AWS"],
            required_experience_years=3,
            required_education="Master's degree in Computer Science, Statistics, or related field",
            language_requirements=[{"language": "English", "level": "Fluent"}]
        ),
        compensation_range="$110k-$150k",
        company_name="TechCorp Inc.",
        status="active"
    )
    jobs.append(job3)
    
    return jobs

def create_sample_candidates():
    """Create sample candidate profiles"""
    
    candidates = []
    
    # Candidate 1: Strong Match
    candidate1 = Candidate(
        id="candidate_001",
        personal_info=PersonalInfo(
            name="John Doe",
            email="john.doe@email.com",
            phone="+1-555-0123",
            location="San Francisco, CA",
            linkedin="https://linkedin.com/in/johndoe",
            github="https://github.com/johndoe"
        ),
        work_experience=[
            WorkExperience(
                company="Tech Innovations LLC",
                role="Senior Software Engineer",
                start_date="2020-01",
                end_date="Present",
                duration_months=60,
                location="San Francisco, CA",
                responsibilities=[
                    "Led development of microservices architecture serving 1M+ users",
                    "Mentored team of 5 junior engineers",
                    "Designed and implemented CI/CD pipeline reducing deployment time by 60%"
                ],
                achievements=[
                    "Reduced API latency by 40%",
                    "Implemented auto-scaling reducing infrastructure costs by 30%"
                ],
                technologies=["Python", "AWS", "Docker", "Kubernetes", "PostgreSQL", "Redis"],
                is_current=True
            ),
            WorkExperience(
                company="StartupXYZ",
                role="Software Engineer",
                start_date="2018-06",
                end_date="2019-12",
                duration_months=18,
                location="San Francisco, CA",
                responsibilities=[
                    "Developed REST APIs using Python/Flask",
                    "Built frontend components with React"
                ],
                technologies=["Python", "React", "MongoDB", "AWS"],
                is_current=False
            )
        ],
        education=[
            Education(
                institution="Massachusetts Institute of Technology",
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                graduation_date="2018-05",
                gpa=3.85,
                honors=["Dean's List", "Summa Cum Laude"]
            )
        ],
        skills=[
            "Python", "JavaScript", "AWS", "Docker", "Kubernetes", "Microservices",
            "React", "PostgreSQL", "Redis", "CI/CD", "Git", "Agile"
        ],
        certifications=[],
        projects=[
            {
                "name": "Open Source Container Orchestration Tool",
                "description": "Contributed to popular Kubernetes tooling",
                "technologies": ["Go", "Kubernetes"]
            }
        ],
        resume_path="/path/to/resume1.pdf",
        resume_filename="john_doe_resume.pdf"
    )
    candidates.append(candidate1)
    
    # Candidate 2: Moderate Match
    candidate2 = Candidate(
        id="candidate_002",
        personal_info=PersonalInfo(
            name="Jane Smith",
            email="jane.smith@email.com",
            phone="+1-555-0124",
            location="Oakland, CA"
        ),
        work_experience=[
            WorkExperience(
                company="Digital Solutions Inc",
                role="Software Developer",
                start_date="2021-03",
                end_date="Present",
                duration_months=44,
                responsibilities=[
                    "Developed backend services using Python",
                    "Worked with Docker containers"
                ],
                technologies=["Python", "Docker", "MySQL", "Git"],
                is_current=True
            )
        ],
        education=[
            Education(
                institution="State University",
                degree="Bachelor of Science",
                field_of_study="Software Engineering",
                graduation_date="2021-05",
                gpa=3.5
            )
        ],
        skills=["Python", "Docker", "MySQL", "Git", "Linux", "CI/CD"],
        resume_path="/path/to/resume2.pdf",
        resume_filename="jane_smith_resume.pdf"
    )
    candidates.append(candidate2)
    
    # Candidate 3: Weak Match
    candidate3 = Candidate(
        id="candidate_003",
        personal_info=PersonalInfo(
            name="Bob Johnson",
            email="bob.johnson@email.com",
            phone="+1-555-0125",
            location="Austin, TX"
        ),
        work_experience=[
            WorkExperience(
                company="Local Tech Co",
                role="Junior Developer",
                start_date="2022-06",
                end_date="Present",
                duration_months=30,
                responsibilities=[
                    "Fixed bugs in legacy codebase",
                    "Wrote unit tests"
                ],
                technologies=["Java", "Spring", "MySQL"],
                is_current=True
            )
        ],
        education=[
            Education(
                institution="Community College",
                degree="Associate Degree",
                field_of_study="Computer Programming",
                graduation_date="2022-05"
            )
        ],
        skills=["Java", "Spring", "MySQL", "Git"],
        resume_path="/path/to/resume3.pdf",
        resume_filename="bob_johnson_resume.pdf"
    )
    candidates.append(candidate3)
    
    return candidates

def create_sample_evaluations(candidates, jobs):
    """Create sample evaluation results"""
    
    evaluations = []
    
    # Evaluation for Candidate 1 (Strong Match)
    eval1 = EvaluationResult(
        candidate_id="candidate_001",
        job_id="job_001",
        evaluation_id="eval_001",
        overall_score=91.5,
        skills_evaluation=SkillsEvaluation(
            overall_match_percentage=92.0,
            required_skills_match=95.0,
            preferred_skills_match=85.0,
            matched_skills=["Python", "AWS", "Docker", "Kubernetes", "Microservices"],
            missing_skills=[],
            transferable_skills=["React experience from previous role"],
            bonus_skills=["Redis", "PostgreSQL"],
            rationale="Candidate demonstrates exceptional technical skills with 6+ years of relevant experience. Strong match on all required skills with proven expertise in cloud architecture and microservices.",
            strengths=[
                "Deep experience with AWS and Kubernetes",
                "Leadership and mentoring experience",
                "Proven track record of performance optimization"
            ],
            gaps=[],
            confidence_score=0.95
        ),
        cultural_evaluation=CulturalFitEvaluation(
            overall_cultural_fit_score=88.0,
            dimensional_scores={
                "Collaboration": 0.90,
                "Innovation": 0.85,
                "Fast-paced": 0.88,
                "Flat": 0.87,
                "Mission-driven": 0.85
            },
            rationale="Strong cultural alignment. Background shows preference for collaborative, fast-paced startup environments with focus on innovation and technical excellence.",
            evidence=[
                "Worked in startup environments",
                "Led cross-functional initiatives",
                "Open source contributions show community engagement"
            ],
            alignment_areas=["Team collaboration", "Innovation focus", "Technical excellence"],
            potential_concerns=[],
            interview_discussion_points=["Career growth expectations", "Team leadership style"],
            confidence_score=0.88
        ),
        experience_score=95.0,
        recommendation=RecommendationType.STRONG_MATCH,
        tier="strong_match",
        executive_summary="Exceptional candidate with strong technical skills and excellent cultural fit. Highly recommended for immediate interview.",
        key_highlights=[
            "8 years of relevant software engineering experience",
            "Strong AWS and Kubernetes expertise",
            "Proven leadership and mentoring capabilities",
            "Excellent cultural fit for collaborative, fast-paced environment"
        ],
        recommended_next_steps=["Schedule technical interview", "Arrange team meet-and-greet"],
        interview_focus_areas=["System design capabilities", "Leadership experience", "Long-term career goals"]
    )
    evaluations.append(eval1)
    
    # Evaluation for Candidate 2 (Moderate Match)
    eval2 = EvaluationResult(
        candidate_id="candidate_002",
        job_id="job_001",
        evaluation_id="eval_002",
        overall_score=76.0,
        skills_evaluation=SkillsEvaluation(
            overall_match_percentage=78.0,
            required_skills_match=75.0,
            preferred_skills_match=70.0,
            matched_skills=["Python", "Docker"],
            missing_skills=["AWS", "Kubernetes", "Microservices"],
            transferable_skills=["Container experience with Docker"],
            bonus_skills=[],
            rationale="Solid foundational skills but lacks some key requirements. Has 3.5 years experience which is below the 5-year requirement. Missing critical cloud and orchestration experience.",
            strengths=["Strong Python skills", "Docker experience"],
            gaps=["Limited AWS experience", "No Kubernetes experience", "Less experience than required"],
            confidence_score=0.82
        ),
        cultural_evaluation=CulturalFitEvaluation(
            overall_cultural_fit_score=72.0,
            dimensional_scores={
                "Collaboration": 0.75,
                "Innovation": 0.70,
                "Fast-paced": 0.72,
                "Flat": 0.68,
                "Mission-driven": 0.75
            },
            rationale="Reasonable cultural fit with some areas to explore. Limited information on work style preferences and collaboration patterns.",
            evidence=["Worked in mid-size company", "Backend development focus"],
            alignment_areas=["Technical focus"],
            potential_concerns=["Limited startup experience", "Unclear collaboration style"],
            interview_discussion_points=["Work style preferences", "Learning agility", "Interest in cloud technologies"],
            confidence_score=0.70
        ),
        experience_score=70.0,
        recommendation=RecommendationType.MODERATE_MATCH,
        tier="moderate_match",
        executive_summary="Promising candidate with solid foundation but notable skill gaps. Recommend recruiter review to assess growth potential and learning ability.",
        key_highlights=[
            "3.5 years of software development experience",
            "Strong Python and Docker skills",
            "Growth potential"
        ],
        concerns=[
            "Below required experience level",
            "Missing AWS and Kubernetes experience",
            "Limited system design experience"
        ],
        recommended_next_steps=["Recruiter phone screen", "Assess learning agility and motivation"],
        interview_focus_areas=["Learning experiences", "Interest in cloud technologies", "Career goals"]
    )
    evaluations.append(eval2)
    
    return evaluations

def create_sample_interviews(candidates):
    """Create sample interview slots"""
    
    interviews = []
    
    # Interview 1: Upcoming
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    interview1 = InterviewSlot(
        id="interview_001",
        candidate_id="candidate_001",
        job_id="job_001",
        candidate_name="John Doe",
        candidate_email="john.doe@email.com",
        candidate_phone="+1-555-0123",
        interview_type=InterviewType.TECHNICAL,
        round_number=1,
        start_time=tomorrow.replace(hour=10, minute=0, second=0, microsecond=0),
        end_time=tomorrow.replace(hour=11, minute=0, second=0, microsecond=0),
        duration_minutes=60,
        timezone="America/Los_Angeles",
        interviewer_email="tech.lead@techcorp.com",
        interviewer_name="Alice Johnson",
        attendees=[
            Attendee(
                email="tech.lead@techcorp.com",
                name="Alice Johnson",
                role="interviewer",
                response_status="accepted"
            )
        ],
        meeting_platform=MeetingPlatform.GOOGLE_MEET,
        video_conference_link="https://meet.google.com/abc-defg-hij",
        status=InterviewStatus.CONFIRMED,
        title="Technical Interview - Senior Software Engineer",
        description="Technical interview focusing on system design and problem-solving",
        focus_areas=["System design", "Microservices architecture", "AWS experience", "Problem-solving"],
        required_materials=["Resume", "Portfolio projects"]
    )
    interviews.append(interview1)
    
    # Interview 2: Completed
    yesterday = now - timedelta(days=1)
    interview2 = InterviewSlot(
        id="interview_002",
        candidate_id="candidate_002",
        job_id="job_001",
        candidate_name="Jane Smith",
        candidate_email="jane.smith@email.com",
        interview_type=InterviewType.PHONE_SCREEN,
        round_number=1,
        start_time=yesterday.replace(hour=14, minute=0, second=0, microsecond=0),
        end_time=yesterday.replace(hour=14, minute=30, second=0, microsecond=0),
        duration_minutes=30,
        timezone="America/Los_Angeles",
        interviewer_email="recruiter@techcorp.com",
        interviewer_name="Bob Smith",
        meeting_platform=MeetingPlatform.PHONE,
        status=InterviewStatus.COMPLETED,
        completed_at=yesterday.replace(hour=14, minute=30, second=0, microsecond=0),
        rating=3,
        recommendation="maybe",
        notes="Candidate shows promise but needs more experience with required technologies. Recommend for junior role instead.",
        feedback="Good communication skills and enthusiasm. Technical skills are developing but not yet at senior level."
    )
    interviews.append(interview2)
    
    return interviews

def save_to_json(data, filename):
    """Save data to JSON file"""
    output_dir = project_root / "data" / "sample_data"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = output_dir / filename
    
    # Convert Pydantic models to dict
    if isinstance(data, list):
        data_dict = [item.dict() if hasattr(item, 'dict') else item for item in data]
    else:
        data_dict = data.dict() if hasattr(data, 'dict') else data
    
    with open(filepath, 'w') as f:
        json.dump(data_dict, f, indent=2, default=str)
    
    print(f"✓ Saved {filename}")
    return filepath

def seed_database():
    """Seed database with sample data"""
    
    print("=" * 70)
    print("Seeding Database with Sample Data")
    print("=" * 70)
    print()
    
    # Create sample data
    print("Creating sample jobs...")
    jobs = create_sample_jobs()
    save_to_json(jobs, "sample_jobs.json")
    print(f"  Created {len(jobs)} job descriptions")
    print()
    
    print("Creating sample candidates...")
    candidates = create_sample_candidates()
    save_to_json(candidates, "sample_candidates.json")
    print(f"  Created {len(candidates)} candidate profiles")
    print()
    
    print("Creating sample evaluations...")
    evaluations = create_sample_evaluations(candidates, jobs)
    save_to_json(evaluations, "sample_evaluations.json")
    print(f"  Created {len(evaluations)} evaluation results")
    print()
    
    print("Creating sample interviews...")
    interviews = create_sample_interviews(candidates)
    save_to_json(interviews, "sample_interviews.json")
    print(f"  Created {len(interviews)} interview slots")
    print()
    
    print("=" * 70)
    print("✅ Database Seeding Complete!")
    print("=" * 70)
    print()
    print("Sample data files created in: data/sample_data/")
    print()
    print("Files created:")
    print("  • sample_jobs.json")
    print("  • sample_candidates.json")
    print("  • sample_evaluations.json")
    print("  • sample_interviews.json")
    print()
    print("You can use this data for:")
    print("  - Testing the API endpoints")
    print("  - Developing the dashboard")
    print("  - Testing agent workflows")
    print("  - Demo presentations")

if __name__ == '__main__':
    seed_database()