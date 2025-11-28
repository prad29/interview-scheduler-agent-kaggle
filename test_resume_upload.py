#!/usr/bin/env python3
"""
Test script to diagnose resume upload and processing issues
Run this to test if the system works end-to-end
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.pdf_parser import extract_text_from_pdf
from agents.orchestrator_agent import OrchestratorAgent
import json

def test_resume_processing():
    """Test the complete resume processing workflow"""

    print("=" * 60)
    print("TESTING RESUME PROCESSING SYSTEM")
    print("=" * 60)

    # Step 1: Test PDF extraction
    print("\n[1/5] Testing PDF extraction...")
    resume_path = "/Users/souveek/Downloads/MD_AAMIR_KHAN_5.3_YOE.pdf"

    try:
        text = extract_text_from_pdf(resume_path)
        print(f"✅ SUCCESS: Extracted {len(text)} characters")
        print(f"   Preview: {text[:100]}...")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

    # Step 2: Load job description
    print("\n[2/5] Loading job description...")
    jobs_file = Path("data/jobs/jobs_list.json")

    try:
        with open(jobs_file, 'r') as f:
            jobs = json.load(f)

        job_data = jobs[0]  # Get first job
        job_description = {
            'title': job_data.get('title'),
            'required_skills': job_data.get('requirements', {}).get('required_skills', []),
            'preferred_skills': job_data.get('requirements', {}).get('preferred_skills', []),
            'experience_level': job_data.get('experience_level'),
            'description': job_data.get('description'),
            'responsibilities': job_data.get('responsibilities', [])
        }
        company_culture = job_data.get('company_culture', {})

        print(f"✅ SUCCESS: Loaded job '{job_description['title']}'")
        print(f"   Required skills: {len(job_description['required_skills'])}")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

    # Step 3: Prepare resume data
    print("\n[3/5] Preparing resume data...")
    resumes = [{
        'filename': 'MD_AAMIR_KHAN_5.3_YOE.pdf',
        'resume_content': text
    }]
    print(f"✅ SUCCESS: Prepared {len(resumes)} resume(s)")

    # Step 4: Initialize orchestrator
    print("\n[4/5] Initializing orchestrator agent...")
    try:
        orchestrator = OrchestratorAgent()
        print("✅ SUCCESS: Orchestrator initialized")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

    # Step 5: Run processing
    print("\n[5/5] Running AI evaluation (this may take 30-60 seconds)...")

    async def run_processing():
        return await orchestrator.process({
            'resumes': resumes,
            'job_description': job_description,
            'company_culture': company_culture,
            'interviewer_email': None
        })

    try:
        result = asyncio.run(run_processing())

        if result['status'] == 'success':
            print("✅ SUCCESS: Processing completed!")

            summary = result.get('processing_summary', {})
            print(f"\n   📊 Processing Summary:")
            print(f"      Total resumes: {summary.get('total_resumes', 0)}")
            print(f"      Successfully parsed: {summary.get('successfully_parsed', 0)}")
            print(f"      Qualified candidates: {summary.get('qualified_candidates', 0)}")

            if result.get('ranked_candidates'):
                candidate = result['ranked_candidates'][0]
                print(f"\n   🏆 Top Candidate:")
                print(f"      Name: {candidate['name']}")
                print(f"      Overall Score: {candidate['overall_score']}%")
                print(f"      Skills Match: {candidate['skills_match_score']}%")
                print(f"      Cultural Fit: {candidate['cultural_fit_score']}%")
                print(f"      Tier: {candidate['tier']}")
                print(f"      Matched Skills: {', '.join(candidate['matched_skills'][:5])}")

            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED - SYSTEM IS WORKING!")
            print("=" * 60)
            return True
        else:
            print(f"❌ FAILED: {result.get('message', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        print("\nFull error trace:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_resume_processing()
    sys.exit(0 if success else 1)
