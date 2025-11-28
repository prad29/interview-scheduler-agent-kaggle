#!/usr/bin/env python3
"""
Manually process a resume and save to database
Use this if the Streamlit upload isn't working
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime
import uuid

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.pdf_parser import extract_text_from_pdf
from agents.orchestrator_agent import OrchestratorAgent
from storage.database import SessionLocal, CandidateModel, EvaluationModel, Base, engine
import json

def manually_process_and_save():
    """Process a resume and save to database"""

    print("=" * 70)
    print("MANUALLY PROCESSING AND SAVING RESUME TO DATABASE")
    print("=" * 70)

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Step 1: Extract resume
    resume_path = "/Users/souveek/Downloads/MD_AAMIR_KHAN_5.3_YOE.pdf"
    print(f"\n[1/5] Extracting resume from: {resume_path}")

    try:
        text = extract_text_from_pdf(resume_path)
        print(f"✅ Extracted {len(text)} characters")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return

    # Step 2: Load job description
    print("\n[2/5] Loading job description...")
    jobs_file = Path("data/jobs/jobs_list.json")

    with open(jobs_file, 'r') as f:
        jobs = json.load(f)

    job_data = jobs[0]  # First job - Fullstack Developer
    job_id = job_data['id']

    job_description = {
        'title': job_data.get('title'),
        'required_skills': job_data.get('requirements', {}).get('required_skills', []),
        'preferred_skills': job_data.get('requirements', {}).get('preferred_skills', []),
        'experience_level': job_data.get('experience_level'),
        'description': job_data.get('description'),
        'responsibilities': job_data.get('responsibilities', [])
    }
    company_culture = job_data.get('company_culture', {})

    print(f"✅ Loaded job: {job_description['title']} ({job_id})")

    # Step 3: Prepare resume
    print("\n[3/5] Preparing resume data...")
    resumes = [{
        'filename': 'MD_AAMIR_KHAN_5.3_YOE.pdf',
        'resume_content': text,
        'file_path': resume_path
    }]

    # Step 4: Process with orchestrator
    print("\n[4/5] Processing with AI agents (30-60 seconds)...")
    orchestrator = OrchestratorAgent()

    async def run_processing():
        return await orchestrator.process({
            'resumes': resumes,
            'job_description': job_description,
            'company_culture': company_culture,
            'interviewer_email': None
        })

    result = asyncio.run(run_processing())

    if result['status'] != 'success':
        print(f"❌ Processing failed: {result.get('message')}")
        return

    print("✅ Processing completed")

    # Step 5: Save to database
    print("\n[5/5] Saving to database...")
    session = SessionLocal()

    try:
        saved_count = 0

        for candidate_result in result.get('ranked_candidates', []):
            candidate_id = str(uuid.uuid4())

            # Create candidate record
            candidate = CandidateModel(
                id=candidate_id,
                job_id=job_id,
                personal_info=candidate_result.get('candidate_data', {}).get('personal_info', {}),
                work_experience=candidate_result.get('candidate_data', {}).get('work_experience', []),
                education=candidate_result.get('candidate_data', {}).get('education', []),
                skills=candidate_result.get('matched_skills', []),
                resume_filename=resumes[0]['filename'],
                resume_path=resumes[0]['file_path'],
                status='screening',
                created_at=datetime.now()
            )
            session.add(candidate)

            # Create evaluation record
            evaluation = EvaluationModel(
                id=str(uuid.uuid4()),
                candidate_id=candidate_id,
                job_id=job_id,
                overall_score=candidate_result.get('overall_score', 0) / 100.0,
                skills_match_score=candidate_result.get('skills_match_score', 0) / 100.0,
                cultural_fit_score=candidate_result.get('cultural_fit_score', 0) / 100.0,
                experience_score=candidate_result.get('experience_score', 0) / 100.0,
                recommendation=candidate_result.get('recommendation', 'weak_match'),
                tier=candidate_result.get('tier', 'weak_match'),
                skills_evaluation={
                    'matched_skills': candidate_result.get('matched_skills', []),
                    'missing_skills': candidate_result.get('missing_skills', []),
                    'rationale': candidate_result.get('skills_rationale', '')
                },
                cultural_evaluation={
                    'rationale': candidate_result.get('cultural_rationale', ''),
                    'dimensional_scores': candidate_result.get('dimensional_scores', {})
                },
                evaluated_at=datetime.now(),
                created_at=datetime.now()
            )
            session.add(evaluation)
            saved_count += 1

        session.commit()
        print(f"✅ Saved {saved_count} candidate(s) to database")

        # Show details
        print("\n" + "=" * 70)
        print("CANDIDATE DETAILS SAVED:")
        print("=" * 70)

        candidate_result = result['ranked_candidates'][0]
        print(f"\n👤 Name: {candidate_result['name']}")
        print(f"📧 Email: {candidate_result['email']}")
        print(f"📊 Overall Score: {candidate_result['overall_score']}%")
        print(f"🎯 Skills Match: {candidate_result['skills_match_score']}%")
        print(f"💼 Cultural Fit: {candidate_result['cultural_fit_score']}%")
        print(f"🏆 Tier: {candidate_result['tier']}")
        print(f"✅ Matched Skills: {', '.join(candidate_result['matched_skills'][:8])}")
        print(f"⚠️  Missing Skills: {', '.join(candidate_result['missing_skills'][:5])}")

        print("\n" + "=" * 70)
        print("✅ SUCCESS! Now refresh your Streamlit dashboard to see the candidate.")
        print("=" * 70)

    except Exception as e:
        session.rollback()
        print(f"❌ Database save failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    manually_process_and_save()
