"""
Main Streamlit Dashboard Application

This is the entry point for the Intelligent Recruitment System dashboard.
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dashboard.pages import render_home_page, render_candidates_page, render_interviews_page
from dashboard.pages.jobs import render_jobs_page

# Page configuration
st.set_page_config(
    page_title="Intelligent Recruitment System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    
    /* Subtitle styling */
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    
    /* Metric card styling */
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    
    /* Success message */
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        color: #155724;
    }
    
    /* Warning message */
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.25rem;
        padding: 1rem;
        color: #856404;
    }
    
    /* Info message */
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.25rem;
        padding: 1rem;
        color: #0c5460;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
        font-weight: 600;
        padding: 0.5rem 1rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Table styling */
    .dataframe {
        font-size: 0.9rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = {
        'name': 'Admin User',
        'email': 'admin@recruitment.ai',
        'role': 'Recruiter'
    }

if 'selected_job' not in st.session_state:
    st.session_state.selected_job = None

if 'selected_candidate' not in st.session_state:
    st.session_state.selected_candidate = None

# Sidebar
with st.sidebar:
    # Logo/Header
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <h1 style='color: #1f77b4; margin: 0;'>🤖</h1>
        <h2 style='margin: 0; font-size: 1.5rem;'>Recruitment AI</h2>
        <p style='color: #666; font-size: 0.9rem;'>Intelligent Hiring System</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Navigation
    st.markdown("### 📍 Navigation")
    
    page = st.radio(
        "Go to",
        ["🏠 Home", "📋 Jobs", "👥 Candidates", "📅 Interviews"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # User info
    st.markdown("### 👤 User Profile")
    st.markdown(f"**{st.session_state.user['name']}**")
    st.caption(f"{st.session_state.user['role']}")
    st.caption(f"✉️ {st.session_state.user['email']}")
    
    st.divider()
    
    # System status
    st.markdown("### ⚙️ System Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("API", "🟢 Online", delta=None)
    
    with col2:
        st.metric("Agents", "🟢 Ready", delta=None)
    
    # Quick stats
    st.markdown("### 📊 Quick Stats")

    # Fetch real metrics from database
    try:
        from dashboard.services import get_metrics
        metrics = get_metrics()

        st.metric("Active Jobs", metrics.get('active_jobs', 0))
        st.metric("Total Candidates", metrics.get('total_candidates', 0), delta=f"{metrics.get('candidates_delta', 0)} new")
        st.metric("Scheduled Interviews", metrics.get('interviews_scheduled', 0), delta=f"{metrics.get('interviews_delta', 0)} today")
    except Exception as e:
        # Fallback to default values if there's an error
        st.metric("Active Jobs", "0")
        st.metric("Total Candidates", "0")
        st.metric("Scheduled Interviews", "0")
    
    st.divider()
    
    # Help section
    with st.expander("ℹ️ Help & Info"):
        st.markdown("""
        **Quick Guide:**
        
        1. **Jobs** - Create and manage job descriptions
        2. **Candidates** - Upload resumes and view rankings
        3. **Interviews** - Schedule and manage interviews
        
        **Need Help?**
        - 📧 support@recruitment.ai
        - 📚 [Documentation](https://docs.recruitment.ai)
        - 💬 [Support Chat](https://chat.recruitment.ai)
        """)
    
    # Version info
    st.caption("Version 1.0.0 | © 2024")

# Main content area
def main():
    """Main application logic"""
    
    # Extract page name without emoji
    page_name = page.split(" ", 1)[1] if " " in page else page
    
    # Route to appropriate page
    if "Home" in page:
        render_home_page()
    
    elif "Jobs" in page:
        render_jobs_page()
    
    elif "Candidates" in page:
        render_candidates_page()
    
    elif "Interviews" in page:
        render_interviews_page()
    
    else:
        st.error("Page not found!")

# Run the app
if __name__ == "__main__":
    main()