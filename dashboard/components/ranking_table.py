import streamlit as st
import pandas as pd
from typing import List, Dict, Any
import plotly.express as px

def render_ranking_table(candidates: List[Dict[str, Any]], show_filters: bool = True):
    """
    Render candidates ranking table
    
    Args:
        candidates: List of candidate dictionaries
        show_filters: Whether to show filter options
    """
    if not candidates:
        st.info("No candidates to display")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(candidates)
    
    # Filters
    if show_filters:
        st.markdown("### 🔍 Filters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tier_filter = st.multiselect(
                "Tier",
                options=['strong_match', 'moderate_match', 'weak_match'],
                default=['strong_match', 'moderate_match', 'weak_match']
            )
        
        with col2:
            min_score = st.slider(
                "Minimum Overall Score",
                min_value=0,
                max_value=100,
                value=0,
                step=5
            )
        
        with col3:
            sort_by = st.selectbox(
                "Sort By",
                options=[
                    'overall_score',
                    'skills_match_score',
                    'cultural_fit_score',
                    'name'
                ],
                index=0
            )
        
        # Apply filters
        df = df[df['tier'].isin(tier_filter)]
        df = df[df['overall_score'] >= min_score]
        df = df.sort_values(by=sort_by, ascending=False)
    
    # Display count
    st.markdown(f"**Showing {len(df)} candidates**")
    
    # Score distribution chart
    with st.expander("📊 Score Distribution", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # Histogram of overall scores
            fig1 = px.histogram(
                df,
                x='overall_score',
                nbins=20,
                title='Overall Score Distribution',
                labels={'overall_score': 'Overall Score (%)'},
                color_discrete_sequence=['#1f77b4']
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Tier distribution pie chart
            tier_counts = df['tier'].value_counts()
            fig2 = px.pie(
                values=tier_counts.values,
                names=tier_counts.index,
                title='Candidates by Tier',
                color_discrete_sequence=['#2ecc71', '#f39c12', '#e74c3c']
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    # Main table
    st.markdown("### 📋 Candidate Rankings")
    
    # Prepare display DataFrame
    display_df = df[[
        'name',
        'email',
        'overall_score',
        'skills_match_score',
        'cultural_fit_score',
        'tier'
    ]].copy()
    
    # Format columns
    display_df['overall_score'] = display_df['overall_score'].apply(lambda x: f"{x:.1f}%")
    display_df['skills_match_score'] = display_df['skills_match_score'].apply(lambda x: f"{x:.1f}%")
    display_df['cultural_fit_score'] = display_df['cultural_fit_score'].apply(lambda x: f"{x:.1f}%")
    
    # Rename columns for display
    display_df.columns = [
        'Name',
        'Email',
        'Overall Score',
        'Skills Match',
        'Cultural Fit',
        'Tier'
    ]
    
    # Style the tier column
    def style_tier(val):
        if val == 'strong_match':
            return 'background-color: #d4edda; color: #155724;'
        elif val == 'moderate_match':
            return 'background-color: #fff3cd; color: #856404;'
        else:
            return 'background-color: #f8d7da; color: #721c24;'
    
    # Display table with styling
    st.dataframe(
        display_df.style.applymap(
            style_tier,
            subset=['Tier']
        ),
        use_container_width=True,
        height=400
    )
    
    # Export options
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    
    with col2:
        # Convert to CSV for download
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="candidates_ranking.csv",
            mime="text/csv"
        )

def render_comparison_table(candidates: List[Dict[str, Any]]):
    """
    Render a detailed comparison table for selected candidates
    
    Args:
        candidates: List of candidate dictionaries to compare
    """
    if not candidates:
        st.warning("No candidates selected for comparison")
        return
    
    st.markdown("### 🔄 Candidate Comparison")
    
    # Create comparison DataFrame
    comparison_data = []
    
    for candidate in candidates:
        comparison_data.append({
            'Name': candidate.get('name', 'N/A'),
            'Overall': f"{candidate.get('overall_score', 0):.1f}%",
            'Skills': f"{candidate.get('skills_match_score', 0):.1f}%",
            'Cultural': f"{candidate.get('cultural_fit_score', 0):.1f}%",
            'Experience': f"{candidate.get('experience_score', 0):.1f}%",
            'Tier': candidate.get('tier', 'N/A'),
            'Matched Skills': len(candidate.get('matched_skills', [])),
            'Missing Skills': len(candidate.get('missing_skills', []))
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Transpose for better comparison view
    comparison_df = comparison_df.set_index('Name').T
    
    st.dataframe(comparison_df, use_container_width=True)
    
    # Radar chart comparison
    st.markdown("#### 📊 Skills Comparison Radar Chart")
    
    # Prepare data for radar chart
    categories = ['Overall', 'Skills', 'Cultural', 'Experience']
    
    fig = px.line_polar(
        r=[
            [c.get('overall_score', 0), c.get('skills_match_score', 0),
             c.get('cultural_fit_score', 0), c.get('experience_score', 0)]
            for c in candidates
        ],
        theta=categories,
        line_close=True
    )
    
    fig.update_traces(fill='toself')
    st.plotly_chart(fig, use_container_width=True)