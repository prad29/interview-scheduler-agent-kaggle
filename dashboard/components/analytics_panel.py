import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List
import pandas as pd

def render_analytics_panel(metrics: Dict[str, Any], candidates: List[Dict[str, Any]] = None):
    """
    Render analytics dashboard with key metrics and visualizations
    
    Args:
        metrics: Dictionary containing system metrics
        candidates: Optional list of candidates for additional analytics
    """
    st.markdown("## 📊 Analytics Dashboard")
    
    # Key Metrics Row
    st.markdown("### 📈 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Candidates",
            value=metrics.get('total_candidates', 0),
            delta=metrics.get('candidates_delta', None)
        )
    
    with col2:
        st.metric(
            label="Strong Matches",
            value=metrics.get('strong_matches', 0),
            delta=metrics.get('strong_matches_delta', None)
        )
    
    with col3:
        st.metric(
            label="Interviews Scheduled",
            value=metrics.get('interviews_scheduled', 0),
            delta=metrics.get('interviews_delta', None)
        )
    
    with col4:
        avg_score = metrics.get('average_match_score', 0)
        st.metric(
            label="Avg Match Score",
            value=f"{avg_score:.1f}%",
            delta=metrics.get('score_delta', None)
        )
    
    st.markdown("---")
    
    # Time Metrics
    st.markdown("### ⏱️ Processing Efficiency")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Avg Processing Time",
            value=f"{metrics.get('avg_processing_time', 0):.1f} min"
        )
    
    with col2:
        st.metric(
            label="Time to Schedule",
            value=f"{metrics.get('time_to_schedule', 0):.1f} hours"
        )
    
    with col3:
        st.metric(
            label="Recruiter Time Saved",
            value=f"{metrics.get('time_saved_percentage', 0):.0f}%"
        )
    
    st.markdown("---")
    
    # Visualizations
    if candidates:
        render_candidate_analytics(candidates)
    
    # Funnel Chart
    st.markdown("### 🔻 Recruitment Funnel")
    render_funnel_chart(metrics)
    
    # Trends
    st.markdown("### 📉 Trends Over Time")
    render_trends_chart(metrics)

def render_candidate_analytics(candidates: List[Dict[str, Any]]):
    """Render detailed candidate analytics"""
    
    df = pd.DataFrame(candidates)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Score distribution by tier
        st.markdown("#### Score Distribution by Tier")
        
        fig = px.box(
            df,
            x='tier',
            y='overall_score',
            color='tier',
            title='Overall Score Distribution by Tier',
            labels={
                'tier': 'Candidate Tier',
                'overall_score': 'Overall Score (%)'
            },
            color_discrete_map={
                'strong_match': '#2ecc71',
                'moderate_match': '#f39c12',
                'weak_match': '#e74c3c'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Skills vs Cultural Fit scatter
        st.markdown("#### Skills vs Cultural Fit")
        
        fig = px.scatter(
            df,
            x='skills_match_score',
            y='cultural_fit_score',
            size='overall_score',
            color='tier',
            hover_data=['name'],
            title='Skills Match vs Cultural Fit',
            labels={
                'skills_match_score': 'Skills Match (%)',
                'cultural_fit_score': 'Cultural Fit (%)'
            },
            color_discrete_map={
                'strong_match': '#2ecc71',
                'moderate_match': '#f39c12',
                'weak_match': '#e74c3c'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Top skills analysis
    st.markdown("#### 🎯 Most Common Skills")
    
    all_skills = []
    for candidate in candidates:
        all_skills.extend(candidate.get('matched_skills', []))
    
    if all_skills:
        skill_counts = pd.Series(all_skills).value_counts().head(10)
        
        fig = px.bar(
            x=skill_counts.index,
            y=skill_counts.values,
            title='Top 10 Most Common Skills Among Candidates',
            labels={'x': 'Skill', 'y': 'Count'},
            color=skill_counts.values,
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)

def render_funnel_chart(metrics: Dict[str, Any]):
    """Render recruitment funnel visualization"""
    
    stages = [
        'Resumes Received',
        'Successfully Parsed',
        'Met Minimum Threshold',
        'Strong Matches',
        'Interviews Scheduled'
    ]
    
    values = [
        metrics.get('total_resumes', 100),
        metrics.get('successfully_parsed', 95),
        metrics.get('qualified_candidates', 60),
        metrics.get('strong_matches', 25),
        metrics.get('interviews_scheduled', 15)
    ]
    
    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textinfo="value+percent initial",
        marker={
            "color": ["#3498db", "#2ecc71", "#f39c12", "#e74c3c", "#9b59b6"]
        }
    ))
    
    fig.update_layout(
        title="Recruitment Pipeline Funnel",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_trends_chart(metrics: Dict[str, Any]):
    """Render trends over time"""
    
    # Sample data - in production, this would come from database
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    
    trend_data = pd.DataFrame({
        'Date': dates,
        'Candidates Processed': [20 + i * 2 for i in range(30)],
        'Strong Matches': [5 + i * 0.5 for i in range(30)],
        'Interviews Scheduled': [3 + i * 0.3 for i in range(30)]
    })
    
    fig = px.line(
        trend_data,
        x='Date',
        y=['Candidates Processed', 'Strong Matches', 'Interviews Scheduled'],
        title='Recruitment Activity Over Time',
        labels={'value': 'Count', 'variable': 'Metric'}
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_performance_metrics(metrics: Dict[str, Any]):
    """Render system performance metrics"""
    
    st.markdown("### ⚡ System Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Processing speed gauge
        st.markdown("#### Processing Speed")
        
        speed = metrics.get('resumes_per_hour', 0)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=speed,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Resumes/Hour"},
            delta={'reference': 80},
            gauge={
                'axis': {'range': [None, 150]},
                'bar': {'color': "#3498db"},
                'steps': [
                    {'range': [0, 50], 'color': "#e74c3c"},
                    {'range': [50, 100], 'color': "#f39c12"},
                    {'range': [100, 150], 'color': "#2ecc71"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 100
                }
            }
        ))
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Agent accuracy
        st.markdown("#### Agent Accuracy")
        
        accuracy = metrics.get('agent_accuracy', 0)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=accuracy,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Accuracy (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#2ecc71"},
                'steps': [
                    {'range': [0, 70], 'color': "#e74c3c"},
                    {'range': [70, 85], 'color': "#f39c12"},
                    {'range': [85, 100], 'color': "#d4edda"}
                ]
            }
        ))
        
        st.plotly_chart(fig, use_container_width=True)