import streamlit as st
from typing import Dict, Any, Optional

def render_candidate_card(candidate_data: Dict[str, Any], show_actions: bool = True):
    """
    Render a candidate card component
    
    Args:
        candidate_data: Dictionary containing candidate information
        show_actions: Whether to show action buttons
    """
    # Determine color based on tier/score
    overall_score = candidate_data.get('overall_score', 0)
    
    if overall_score >= 85:
        color = "green"
        tier_emoji = "🌟"
    elif overall_score >= 70:
        color = "orange"
        tier_emoji = "⭐"
    else:
        color = "red"
        tier_emoji = "📋"
    
    # Create card container
    with st.container():
        st.markdown(f"""
        <div style="
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid {color};
            background-color: #f8f9fa;
            margin-bottom: 15px;
        ">
        </div>
        """, unsafe_allow_html=True)
        
        # Header with name and score
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"### {tier_emoji} {candidate_data.get('name', 'Unknown')}")
            st.caption(f"📧 {candidate_data.get('email', 'N/A')}")
            if candidate_data.get('phone'):
                st.caption(f"📱 {candidate_data.get('phone')}")
        
        with col2:
            st.metric(
                label="Overall Score",
                value=f"{overall_score}%",
                delta=None
            )
        
        # Score breakdown
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            skills_score = candidate_data.get('skills_match_score', 0)
            st.metric("Skills Match", f"{skills_score}%")
        
        with col2:
            cultural_score = candidate_data.get('cultural_fit_score', 0)
            st.metric("Cultural Fit", f"{cultural_score}%")
        
        with col3:
            exp_score = candidate_data.get('experience_score', 0)
            st.metric("Experience", f"{exp_score}%")
        
        # Key highlights
        st.markdown("#### 💡 Key Highlights")
        matched_skills = candidate_data.get('matched_skills', [])
        if matched_skills:
            # Show top 5 skills
            skills_display = matched_skills[:5]
            skills_html = " ".join([
                f'<span style="background-color: #e8f4f8; padding: 5px 10px; border-radius: 15px; margin: 2px; display: inline-block;">{skill}</span>'
                for skill in skills_display
            ])
            st.markdown(skills_html, unsafe_allow_html=True)
        else:
            st.info("No matched skills available")
        
        # Missing skills (if any)
        missing_skills = candidate_data.get('missing_skills', [])
        if missing_skills and len(missing_skills) > 0:
            st.markdown("#### ⚠️ Skill Gaps")
            gaps_display = missing_skills[:3]
            gaps_html = " ".join([
                f'<span style="background-color: #ffe8e8; padding: 5px 10px; border-radius: 15px; margin: 2px; display: inline-block;">{skill}</span>'
                for skill in gaps_display
            ])
            st.markdown(gaps_html, unsafe_allow_html=True)
        
        # Tier badge
        tier = candidate_data.get('tier', 'weak_match')
        tier_display = {
            'strong_match': '🟢 Strong Match',
            'moderate_match': '🟡 Moderate Match',
            'weak_match': '🔴 Weak Match'
        }
        st.markdown(f"**Status:** {tier_display.get(tier, tier)}")
        
        # Action buttons
        if show_actions:
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 View Details", key=f"view_{candidate_data.get('id')}"):
                    st.session_state['selected_candidate'] = candidate_data.get('id')
                    st.rerun()
            
            with col2:
                if st.button("📅 Schedule Interview", key=f"schedule_{candidate_data.get('id')}"):
                    st.session_state['schedule_candidate'] = candidate_data.get('id')
                    st.rerun()
            
            with col3:
                if st.button("📥 Download Report", key=f"download_{candidate_data.get('id')}"):
                    # TODO: Implement report download
                    st.success("Report download initiated!")

def render_candidate_detail(candidate_data: Dict[str, Any]):
    """
    Render detailed candidate information
    
    Args:
        candidate_data: Dictionary containing full candidate information
    """
    st.markdown(f"## {candidate_data.get('name', 'Unknown Candidate')}")
    
    # Basic information
    with st.expander("📋 Basic Information", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Email:**", candidate_data.get('email', 'N/A'))
            st.write("**Phone:**", candidate_data.get('phone', 'N/A'))
        
        with col2:
            st.write("**Candidate ID:**", candidate_data.get('id', 'N/A'))
            st.write("**Resume Index:**", candidate_data.get('resume_index', 'N/A'))
    
    # Scores
    with st.expander("📊 Evaluation Scores", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Overall", f"{candidate_data.get('overall_score', 0)}%")
        with col2:
            st.metric("Skills", f"{candidate_data.get('skills_match_score', 0)}%")
        with col3:
            st.metric("Cultural Fit", f"{candidate_data.get('cultural_fit_score', 0)}%")
        with col4:
            st.metric("Experience", f"{candidate_data.get('experience_score', 0)}%")
    
    # Skills Analysis
    with st.expander("🎯 Skills Analysis", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**✅ Matched Skills**")
            matched = candidate_data.get('matched_skills', [])
            if matched:
                for skill in matched:
                    st.markdown(f"- {skill}")
            else:
                st.info("No matched skills")
        
        with col2:
            st.markdown("**❌ Missing Skills**")
            missing = candidate_data.get('missing_skills', [])
            if missing:
                for skill in missing:
                    st.markdown(f"- {skill}")
            else:
                st.success("No missing critical skills")
    
    # Skills Rationale
    with st.expander("💭 Skills Matching Rationale"):
        rationale = candidate_data.get('skills_rationale', 'No rationale available')
        st.write(rationale)
    
    # Cultural Fit Analysis
    with st.expander("🤝 Cultural Fit Analysis", expanded=True):
        dimensional_scores = candidate_data.get('dimensional_scores', {})
        
        if dimensional_scores:
            for dimension, score in dimensional_scores.items():
                st.progress(score, text=f"{dimension}: {score*100:.0f}%")
        else:
            st.info("No dimensional scores available")
        
        st.markdown("**Cultural Fit Rationale:**")
        cultural_rationale = candidate_data.get('cultural_rationale', 'No rationale available')
        st.write(cultural_rationale)
    
    # Work Experience
    with st.expander("💼 Work Experience"):
        candidate_profile = candidate_data.get('candidate_data', {})
        work_exp = candidate_profile.get('work_experience', [])
        
        if work_exp:
            for idx, exp in enumerate(work_exp, 1):
                st.markdown(f"**{idx}. {exp.get('role', 'N/A')} at {exp.get('company', 'N/A')}**")
                st.caption(f"{exp.get('start_date', 'N/A')} - {exp.get('end_date', 'Present')}")
                
                responsibilities = exp.get('responsibilities', [])
                if responsibilities:
                    for resp in responsibilities:
                        st.markdown(f"- {resp}")
                
                st.markdown("---")
        else:
            st.info("No work experience data available")
    
    # Education
    with st.expander("🎓 Education"):
        education = candidate_profile.get('education', [])
        
        if education:
            for edu in education:
                st.markdown(f"**{edu.get('degree', 'N/A')} - {edu.get('field_of_study', 'N/A')}**")
                st.caption(f"{edu.get('institution', 'N/A')} | {edu.get('graduation_date', 'N/A')}")
                st.markdown("---")
        else:
            st.info("No education data available")