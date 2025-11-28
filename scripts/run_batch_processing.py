#!/usr/bin/env python3
"""
Run batch processing of resumes

This script processes a batch of resumes through the entire recruitment pipeline:
1. Parse resumes
2. Match skills
3. Analyze cultural fit
4. Rank candidates
5. Schedule interviews (optional)

Usage:
    python scripts/run_batch_processing.py --resumes data/sample_resumes/ --job job_001
    python scripts/run_batch_processing.py --resumes data/sample_resumes/ --job job_001 --schedule
    python scripts/run_batch_processing.py --help
"""

import sys
import os
import asyncio
import json
from pathlib import Path
from datetime import datetime
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.orchestrator_agent import OrchestratorAgent
from tools.pdf_parser import extract_text_from_pdf
from tools.docx_parser import extract_text_from_docx
from models.job_description import JobDescription
from utils.logger import setup_logger

# Setup logging
logger = setup_logger("BatchProcessing", "batch_processing.log")

def load_job_description(job_id: str):
    """Load job description from file or database"""
    
    # Try to load from sample data first
    sample_jobs_path = project_root / "data" / "sample_data" / "sample_jobs.json"
    
    if sample_jobs_path.exists():
        with open(sample_jobs_path, 'r') as f:
            jobs = json.load(f)
            for job in jobs:
                if job.get('id') == job_id:
                    logger.info(f"Loaded job description: {job.get('title')}")
                    return job
    
    # If not found, return a default job description
    logger.warning(f"Job {job_id} not found, using default job description")
    return {
        "id": job_id,
        "title": "Senior Software Engineer",
        "description": "We are looking for a Senior Software Engineer...",
        "requirements": {
            "required_skills": ["Python", "AWS", "Docker", "Kubernetes"],
            "preferred_skills": ["React", "TypeScript", "CI/CD"],
            "required_experience_years": 5
        },
        "company_culture": {
            "values": ["Innovation", "Collaboration", "Integrity"],
            "work_style": "Collaborative with autonomy",
            "pace": "Fast-paced",
            "innovation_focus": True
        }
    }

def load_resumes(resumes_path: str):
    """Load resumes from directory or file"""
    
    resumes = []
    path = Path(resumes_path)
    
    if path.is_file():
        # Single file
        files = [path]
    elif path.is_dir():
        # Directory - get all PDF and DOCX files
        files = list(path.glob("*.pdf")) + list(path.glob("*.docx"))
    else:
        logger.error(f"Invalid path: {resumes_path}")
        return []
    
    logger.info(f"Found {len(files)} resume files")
    
    for file_path in files:
        try:
            logger.info(f"Loading: {file_path.name}")
            
            # Extract text based on file type
            if file_path.suffix.lower() == '.pdf':
                text = extract_text_from_pdf(str(file_path))
            elif file_path.suffix.lower() == '.docx':
                text = extract_text_from_docx(str(file_path))
            else:
                logger.warning(f"Unsupported file type: {file_path.suffix}")
                continue
            
            if text and len(text.strip()) > 100:
                resumes.append({
                    "filename": file_path.name,
                    "resume_content": text,
                    "file_path": str(file_path)
                })
                logger.info(f"  ✓ Extracted {len(text)} characters")
            else:
                logger.warning(f"  ✗ Failed to extract text or text too short")
                
        except Exception as e:
            logger.error(f"Error loading {file_path.name}: {str(e)}")
            continue
    
    return resumes

def print_summary(result: dict):
    """Print a summary of the processing results"""
    
    print()
    print("=" * 80)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 80)
    print()
    
    summary = result.get('processing_summary', {})
    
    print(f"Total Resumes Processed:     {summary.get('total_resumes', 0)}")
    print(f"Successfully Parsed:         {summary.get('successfully_parsed', 0)}")
    print(f"Qualified Candidates:        {summary.get('qualified_candidates', 0)}")
    print(f"Interviews Scheduled:        {summary.get('interviews_scheduled', 0)}")
    print()
    
    # Candidate breakdown
    candidates = result.get('ranked_candidates', [])
    
    if candidates:
        strong = len([c for c in candidates if c.get('tier') == 'strong_match'])
        moderate = len([c for c in candidates if c.get('tier') == 'moderate_match'])
        weak = len([c for c in candidates if c.get('tier') == 'weak_match'])
        
        print("Candidate Breakdown:")
        print(f"  🌟 Strong Match:    {strong}")
        print(f"  ⭐ Moderate Match:  {moderate}")
        print(f"  📋 Weak Match:      {weak}")
        print()
    
    # Top candidates
    if candidates:
        print("=" * 80)
        print("TOP CANDIDATES")
        print("=" * 80)
        print()
        
        top_5 = candidates[:5]
        
        for idx, candidate in enumerate(top_5, 1):
            name = candidate.get('name', 'Unknown')
            email = candidate.get('email', 'N/A')
            overall = candidate.get('overall_score', 0)
            skills = candidate.get('skills_match_score', 0)
            cultural = candidate.get('cultural_fit_score', 0)
            tier = candidate.get('tier', 'unknown')
            
            tier_emoji = {
                'strong_match': '🌟',
                'moderate_match': '⭐',
                'weak_match': '📋'
            }.get(tier, '📋')
            
            print(f"{idx}. {tier_emoji} {name}")
            print(f"   Email: {email}")
            print(f"   Overall: {overall:.1f}% | Skills: {skills:.1f}% | Cultural: {cultural:.1f}%")
            print(f"   Tier: {tier}")
            print()
    
    # Scheduled interviews
    interviews = result.get('scheduled_interviews', [])
    
    if interviews:
        print("=" * 80)
        print("SCHEDULED INTERVIEWS")
        print("=" * 80)
        print()
        
        for interview in interviews:
            name = interview.get('candidate_name', 'Unknown')
            start = interview.get('start_time', 'TBD')
            print(f"  📅 {name} - {start}")
        print()

def save_results(result: dict, output_path: str):
    """Save processing results to JSON file"""
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"✓ Results saved to: {output_file}")

async def run_batch_processing(
    resumes_path: str,
    job_id: str,
    interviewer_email: str = None,
    output_path: str = None
):
    """Run batch processing workflow"""
    
    print()
    print("=" * 80)
    print("INTELLIGENT RECRUITMENT SYSTEM - BATCH PROCESSING")
    print("=" * 80)
    print()
    
    start_time = datetime.now()
    
    # Load job description
    print("📋 Loading job description...")
    job_description = load_job_description(job_id)
    print(f"   Job: {job_description.get('title')}")
    print()
    
    # Load resumes
    print("📄 Loading resumes...")
    resumes = load_resumes(resumes_path)
    
    if not resumes:
        logger.error("No resumes loaded. Exiting.")
        return
    
    print(f"   Loaded {len(resumes)} resumes")
    print()
    
    # Initialize orchestrator
    print("🤖 Initializing orchestrator agent...")
    orchestrator = OrchestratorAgent()
    print()
    
    # Process batch
    print("=" * 80)
    print("PROCESSING BATCH...")
    print("=" * 80)
    print()
    print("This may take a few minutes...")
    print()
    
    try:
        result = await orchestrator.process({
            "resumes": resumes,
            "job_description": job_description,
            "company_culture": job_description.get('company_culture', {}),
            "interviewer_email": interviewer_email
        })
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        print()
        print(f"✅ Processing completed in {processing_time:.1f} seconds")
        print()
        
        # Print summary
        print_summary(result)
        
        # Save results if output path provided
        if output_path:
            save_results(result, output_path)
        else:
            # Save to default location
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_output = project_root / "data" / "outputs" / f"batch_results_{timestamp}.json"
            save_results(result, str(default_output))
        
        print()
        print("=" * 80)
        print("✅ BATCH PROCESSING COMPLETE!")
        print("=" * 80)
        print()
        
        return result
        
    except Exception as e:
        logger.error(f"Error during batch processing: {str(e)}")
        print()
        print("=" * 80)
        print("❌ BATCH PROCESSING FAILED")
        print("=" * 80)
        print()
        print(f"Error: {str(e)}")
        print()
        print("Please check the logs for more details.")
        return None

def main():
    """Main function"""
    
    parser = argparse.ArgumentParser(
        description='Run batch processing of resumes through recruitment pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process resumes in a directory
  python scripts/run_batch_processing.py --resumes data/sample_resumes/ --job job_001
  
  # Process and schedule interviews
  python scripts/run_batch_processing.py --resumes data/sample_resumes/ --job job_001 --schedule --interviewer tech.lead@company.com
  
  # Save results to specific file
  python scripts/run_batch_processing.py --resumes data/sample_resumes/ --job job_001 --output results.json
        """
    )
    
    parser.add_argument(
        '--resumes',
        required=True,
        help='Path to resume file or directory containing resumes'
    )
    
    parser.add_argument(
        '--job',
        required=True,
        help='Job ID to match candidates against'
    )
    
    parser.add_argument(
        '--schedule',
        action='store_true',
        help='Automatically schedule interviews for qualified candidates'
    )
    
    parser.add_argument(
        '--interviewer',
        help='Interviewer email address (required if --schedule is used)'
    )
    
    parser.add_argument(
        '--output',
        help='Output file path for results (default: data/outputs/batch_results_TIMESTAMP.json)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.schedule and not args.interviewer:
        parser.error("--interviewer is required when --schedule is used")
    
    # Run batch processing
    asyncio.run(run_batch_processing(
        resumes_path=args.resumes,
        job_id=args.job,
        interviewer_email=args.interviewer if args.schedule else None,
        output_path=args.output
    ))

if __name__ == '__main__':
    main()