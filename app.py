"""LinkedIn Content Pipeline - Main Streamlit App."""

import streamlit as st
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Page configuration
st.set_page_config(
    page_title="LinkedIn Content Pipeline",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0077B5;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("📝 Content Pipeline")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "💡 Add Ideas",
        "⚙️ Settings",
        "🚀 Run Pipeline",
        "📄 Review Content",
        "📊 Analytics"
    ]
)

st.sidebar.markdown("---")

# Demo mode indicator
from config.settings import get_settings
settings = get_settings()

if settings.is_demo_mode:
    st.sidebar.info("🎭 **Demo Mode Active**\n\nUsing mock AI and local storage.")
else:
    if settings.ai_service_primary == "ollama":
        st.sidebar.success("🤖 Ollama AI Connected")
    elif settings.ai_service_primary == "gemini":
        st.sidebar.success("🌟 Gemini AI Connected")

st.sidebar.markdown("---")
st.sidebar.caption("v1.0.0 | [Documentation](https://github.com/blakehow/linkedin-content-pipeline)")

# Route to pages
if page == "🏠 Home":
    from src.ui import home
    home.show()

elif page == "💡 Add Ideas":
    from src.ui import idea_entry
    idea_entry.show()

elif page == "⚙️ Settings":
    from src.ui import settings_page
    settings_page.show()

elif page == "🚀 Run Pipeline":
    from src.ui import pipeline_runner
    pipeline_runner.show()

elif page == "📄 Review Content":
    from src.ui import content_review
    content_review.show()

elif page == "📊 Analytics":
    from src.ui import analytics
    analytics.show()
