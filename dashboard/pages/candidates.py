import streamlit as st
from dashboard.components import render_candidate_card, render_ranking_table, render_candidate_detail
import requests

def render_candidates_page():
    """Render candidates page with search, filter, and detailed views"""
    
    st.title("👥 Candidates")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 All Candidates", "📤 Upload Resumes", "🔍 Advanced Search"])
    
    with tab1:
        render_candidates_list()
    
    with tab2:
        render_upload_interface()
    
    with tab3:
        render_advanced_search()

def render_candidates_list():
    """Render list of all candidates"""

    st.markdown("### Candidate Rankings")

    # Fetch real data from database
    from dashboard.services import get_candidates
    candidates = get_candidates()
    
    # View toggle
    view_type = st.radio(
        "View Type",
        options=["Table View", "Card View"],
        horizontal=True
    )
    
    if view_type == "Table View":
        render_ranking_table(candidates, show_filters=True)
    else:
        # Card view
        st.markdown("---")
        
        # Filters for card view
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search = st.text_input("🔍 Search candidates", placeholder="Name, email, or skills...")
        
        with col2:
            tier_filter = st.selectbox("Filter by Tier", ["All", "Strong Match", "Moderate Match", "Weak Match"])
        
        # Apply filters
        filtered_candidates = candidates
        
        if search:
            filtered_candidates = [
                c for c in filtered_candidates 
                if search.lower() in c.get('name', '').lower() or
                   search.lower() in c.get('email', '').lower()
            ]
        
        if tier_filter != "All":
            tier_map = {
                "Strong Match": "strong_match",
                "Moderate Match": "moderate_match",
                "Weak Match": "weak_match"
            }
            filtered_candidates = [
                c for c in filtered_candidates
                if c.get('tier') == tier_map[tier_filter]
            ]
        
        st.markdown(f"**Showing {len(filtered_candidates)} candidates**")
        
        # Render cards
        for candidate in filtered_candidates:
            render_candidate_card(candidate)
    
    # Check if candidate details should be shown
    if 'selected_candidate' in st.session_state:
        st.markdown("---")
        selected = next(
            (c for c in candidates if c['id'] == st.session_state['selected_candidate']),
            None
        )
        if selected:
            render_candidate_detail(selected)
            
            if st.button("← Back to List"):
                del st.session_state['selected_candidate']
                st.rerun()

def render_upload_interface():
    """Render resume upload interface"""

    st.markdown("### Upload Candidate Resumes")

    # Load available jobs from file
    from pathlib import Path
    import json

    jobs_list_file = Path("data/jobs/jobs_list.json")

    if not jobs_list_file.exists():
        st.warning("⚠️ No job descriptions found. Please create a job description in the Jobs page first.")
        return

    with open(jobs_list_file, 'r') as f:
        jobs = json.load(f)

    if not jobs:
        st.warning("⚠️ No job descriptions found. Please create a job description in the Jobs page first.")
        return

    # Create job options mapping
    job_options = {job['id']: f"{job['title']} ({job['id']})" for job in jobs}

    # Job selection
    job_id = st.selectbox(
        "Select Job Position",
        options=list(job_options.keys()),
        format_func=lambda x: job_options[x]
    )
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Upload resumes (PDF or DOCX)",
        type=['pdf', 'docx'],
        accept_multiple_files=True,
        help="You can upload multiple files at once. Maximum 10MB per file."
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) selected")
        
        # Show file details
        with st.expander("📎 Uploaded Files"):
            for file in uploaded_files:
                st.write(f"- {file.name} ({file.size / 1024:.1f} KB)")
        
        # Options
        col1, col2 = st.columns(2)
        
        with col1:
            auto_schedule = st.checkbox(
                "Automatically schedule interviews for strong matches",
                value=True
            )
        
        with col2:
            interviewer_email = st.text_input(
                "Interviewer Email",
                placeholder="interviewer@company.com"
            )
        
        # Process button
        if st.button("🚀 Process Resumes", type="primary", use_container_width=True):
            with st.spinner("Processing resumes..."):
                # In production, call API endpoint
                process_uploaded_resumes(uploaded_files, job_id, interviewer_email if auto_schedule else None)

def render_advanced_search():
    """Render advanced search interface"""
    
    st.markdown("### Advanced Candidate Search")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Search criteria
        st.markdown("#### Search Criteria")
        
        name_search = st.text_input("Name")
        email_search = st.text_input("Email")
        
        skills_search = st.multiselect(
            "Required Skills",
            options=["Python", "Java", "AWS", "Docker", "Kubernetes", "React", "TypeScript"]
        )
        
        min_score = st.slider("Minimum Overall Score", 0, 100, 70)
    
    with col2:
        # Filters
        st.markdown("#### Additional Filters")
        
        tier_select = st.multiselect(
            "Tier",
            options=["strong_match", "moderate_match", "weak_match"],
            default=["strong_match", "moderate_match"]
        )
        
        experience_range = st.slider(
            "Years of Experience",
            min_value=0,
            max_value=20,
            value=(3, 10)
        )
        
        date_range = st.date_input(
            "Application Date Range",
            value=None
        )
    
    # Search button
    if st.button("🔍 Search", type="primary", use_container_width=True):
        # Fetch filtered results from database
        from dashboard.services import get_candidates

        candidates = get_candidates(
            tier=tier_select[0] if tier_select else None,
            min_score=min_score
        )

        # Apply additional filters
        if name_search:
            candidates = [c for c in candidates if name_search.lower() in c.get('name', '').lower()]

        if email_search:
            candidates = [c for c in candidates if email_search.lower() in c.get('email', '').lower()]

        if skills_search:
            candidates = [
                c for c in candidates
                if any(skill in c.get('matched_skills', []) for skill in skills_search)
            ]

        st.markdown("### Search Results")
        if candidates:
            render_ranking_table(candidates, show_filters=False)
        else:
            st.info("No candidates found matching the criteria")

# Removed get_sample_candidates() - now using real data from data_service

def process_uploaded_resumes(files, job_id: str, interviewer_email: str = None):
    """Process uploaded resumes through orchestrator"""

    import sys
    import asyncio
    from pathlib import Path
    from datetime import datetime
    import uuid

    # Add project root to path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

    from tools.pdf_parser import extract_text_from_pdf
    from tools.docx_parser import extract_text_from_docx
    from agents.orchestrator_agent import OrchestratorAgent
    from storage.database import (
        SessionLocal, CandidateModel, EvaluationModel,
        InterviewModel, Base, engine
    )
    from config import config

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Get job description
        status_text.text("Loading job description...")

        # Try to load from JSON first
        jobs_list_file = Path("data/jobs/jobs_list.json")
        job_description = None
        company_culture = {}

        if jobs_list_file.exists():
            import json
            with open(jobs_list_file, 'r') as f:
                jobs = json.load(f)
                job_data = next((j for j in jobs if j['id'] == job_id), None)

                if job_data:
                    job_description = {
                        'title': job_data.get('title'),
                        'required_skills': job_data.get('requirements', {}).get('required_skills', []),
                        'preferred_skills': job_data.get('requirements', {}).get('preferred_skills', []),
                        'experience_level': job_data.get('experience_level'),
                        'description': job_data.get('description'),
                        'responsibilities': job_data.get('responsibilities', [])
                    }
                    company_culture = job_data.get('company_culture', {})

        if not job_description:
            st.error(f"Job description not found for {job_id}")
            return

        # Save uploaded files and extract text
        status_text.text("Saving uploaded files...")
        resumes = []

        upload_dir = Path(config.RESUME_STORAGE_PATH)
        upload_dir.mkdir(parents=True, exist_ok=True)

        for i, file in enumerate(files):
            try:
                # Generate unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_filename = f"{timestamp}_{file.name}"
                file_path = upload_dir / unique_filename

                # Save file
                with open(file_path, 'wb') as f:
                    f.write(file.getbuffer())

                # Extract text
                status_text.text(f"Extracting text from {file.name}...")

                if file.name.lower().endswith('.pdf'):
                    text = extract_text_from_pdf(str(file_path))
                elif file.name.lower().endswith('.docx'):
                    text = extract_text_from_docx(str(file_path))
                else:
                    st.warning(f"Unsupported file type: {file.name}")
                    continue

                resumes.append({
                    'filename': unique_filename,
                    'resume_content': text,
                    'file_path': str(file_path)
                })

                progress_bar.progress((i + 1) / (len(files) * 2))

            except Exception as e:
                st.error(f"Error processing {file.name}: {str(e)}")
                continue

        if not resumes:
            st.error("No resumes could be processed")
            return

        # Process through orchestrator
        status_text.text("Running AI evaluation (this may take 30-60 seconds)...")

        orchestrator = OrchestratorAgent()

        # Run async orchestrator with spinner
        with st.spinner('🤖 AI agents are analyzing the resume... Please wait...'):
            # Run async orchestrator
            async def run_orchestrator():
                return await orchestrator.process({
                    'resumes': resumes,
                    'job_description': job_description,
                    'company_culture': company_culture,
                    'interviewer_email': interviewer_email
                })

            # Use asyncio.run() which handles the event loop properly
            result = asyncio.run(run_orchestrator())

        progress_bar.progress(1.0)

        if result['status'] == 'success':
            # Save results to database
            status_text.text("Saving results to database...")

            session = SessionLocal()
            try:
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
                        resume_filename=resumes[candidate_result.get('resume_index', 0)]['filename'],
                        resume_path=resumes[candidate_result.get('resume_index', 0)]['file_path'],
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

                # Save scheduled interviews to database
                scheduled_interviews = result.get('scheduled_interviews', [])
                for interview_data in scheduled_interviews:
                    interview = InterviewModel(
                        id=str(uuid.uuid4()),
                        candidate_id=interview_data.get('candidate_id'),
                        job_id=job_id,
                        candidate_name=interview_data.get('candidate_name'),
                        candidate_email=interview_data.get('candidate_email'),
                        start_time=datetime.fromisoformat(interview_data.get('start_time')),
                        end_time=datetime.fromisoformat(interview_data.get('end_time')),
                        duration_minutes=60,
                        interviewer_email=interviewer_email,
                        status=interview_data.get('status', 'scheduled'),
                        calendar_event_id=interview_data.get('calendar_event_id'),
                        created_at=datetime.now()
                    )
                    session.add(interview)

                session.commit()
                status_text.text("")
                st.success(f"✅ Successfully processed and saved {len(files)} resume(s) to database!")

                # Log success
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Successfully saved {len(result.get('ranked_candidates', []))} candidates to database")
                if scheduled_interviews:
                    logger.info(f"Successfully saved {len(scheduled_interviews)} scheduled interviews to database")

            except Exception as e:
                session.rollback()
                st.error(f"⚠️ Results processed but database save failed: {str(e)}")

                # Show error details
                with st.expander("🔍 View Database Error Details"):
                    import traceback
                    st.code(traceback.format_exc())

                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Database save failed: {str(e)}")
                logger.error(traceback.format_exc())
            finally:
                session.close()

            # Show detailed summary
            summary = result.get('processing_summary', {})

            st.info(f"""
            **Processing Summary:**
            - Total resumes uploaded: {summary.get('total_resumes', 0)}
            - Successfully parsed: {summary.get('successfully_parsed', 0)}
            - Qualified candidates: {summary.get('qualified_candidates', 0)}
            - Interviews scheduled: {summary.get('interviews_scheduled', 0)}
            """)

            # Show top candidates
            if result.get('ranked_candidates'):
                st.markdown("### 🏆 Top Candidates")

                for candidate in result['ranked_candidates'][:5]:
                    with st.expander(f"{candidate['name']} - Score: {candidate['overall_score']}%"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write(f"**Email:** {candidate['email']}")
                            st.write(f"**Tier:** {candidate['tier'].replace('_', ' ').title()}")
                            st.write(f"**Skills Match:** {candidate['skills_match_score']}%")

                        with col2:
                            st.write(f"**Cultural Fit:** {candidate['cultural_fit_score']}%")

                            # Handle matched_skills - might be list of strings or list of dicts
                            matched_skills = candidate.get('matched_skills', [])
                            if matched_skills:
                                if isinstance(matched_skills[0], dict):
                                    # If it's a list of dicts, extract the skill names
                                    skill_names = [s.get('skill', str(s)) for s in matched_skills[:5]]
                                else:
                                    # If it's already a list of strings
                                    skill_names = matched_skills[:5]
                                st.write(f"**Matched Skills:** {', '.join(skill_names)}")
                            else:
                                st.write(f"**Matched Skills:** None")

                # Add button to view all candidates
                st.divider()
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.info("💡 **Click 'All Candidates' tab above to see the full candidate list!**")

                # Store flag to potentially auto-switch tabs (if needed)
                st.session_state['candidates_uploaded'] = True

        else:
            st.error(f"❌ Processing failed: {result.get('message', 'Unknown error')}")

    except Exception as e:
        st.error(f"❌ Error during processing: {str(e)}")

        # Show detailed error in expander
        with st.expander("🔍 View Error Details"):
            import traceback
            st.code(traceback.format_exc())

            st.markdown("**Common issues:**")
            st.markdown("- Check if GOOGLE_API_KEY is set in .env file")
            st.markdown("- Ensure the resume is a text-based PDF (not image-based)")
            st.markdown("- Check logs/api.log for detailed error messages")

        # Log to console
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Resume processing failed: {str(e)}")
        logger.error(traceback.format_exc())