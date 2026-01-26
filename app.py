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

# Custom CSS - Dark Professional Theme
st.markdown("""
    <style>
    /* Dark theme colors */
    :root {
        --background-primary: #1a1a1a;
        --background-secondary: #2d2d2d;
        --text-primary: #e0e0e0;
        --text-secondary: #b0b0b0;
        --accent-color: #0077B5;
        --border-color: #404040;
    }

    /* Main content area */
    .stApp {
        background-color: #1a1a1a;
        font-size: 0.9rem;
    }

    /* Reduce header sizes */
    h1 {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        color: #e0e0e0 !important;
        margin-bottom: 1rem !important;
    }

    h2 {
        font-size: 1.3rem !important;
        font-weight: 500 !important;
        color: #d0d0d0 !important;
    }

    h3 {
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        color: #c0c0c0 !important;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #2d2d2d;
    }

    /* Text areas and inputs */
    .stTextArea textarea, .stTextInput input {
        font-size: 0.85rem !important;
        background-color: #2d2d2d !important;
        color: #e0e0e0 !important;
        border: 1px solid #404040 !important;
    }

    /* Buttons */
    .stButton button {
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        border-radius: 4px !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-size: 0.9rem !important;
        background-color: #2d2d2d !important;
    }

    /* Cards and containers */
    [data-testid="stExpander"] {
        background-color: #2d2d2d;
        border: 1px solid #404040;
    }

    /* Markdown text */
    .stMarkdown {
        font-size: 0.85rem;
        color: #e0e0e0;
    }

    /* Reduce spacing */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
    }

    /* Professional metric cards */
    .metric-card {
        background: #2d2d2d;
        padding: 0.75rem;
        border-radius: 4px;
        margin: 0.5rem 0;
        border: 1px solid #404040;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Content Pipeline")
st.sidebar.markdown("---")

# Initialize default page if not set
if "current_page" not in st.session_state:
    st.session_state.current_page = "Add Ideas"

page = st.sidebar.radio(
    "Navigation",
    [
        "Add Ideas",
        "Run Pipeline",
        "Review Content",
        "Analytics",
        "Settings"
    ],
    index=["Add Ideas", "Run Pipeline", "Review Content", "Analytics", "Settings"].index(st.session_state.current_page) if st.session_state.current_page in ["Add Ideas", "Run Pipeline", "Review Content", "Analytics", "Settings"] else 0
)

# Update current page in session state
st.session_state.current_page = page

st.sidebar.markdown("---")

# AI status indicator
from config.settings import get_settings
from src.data.storage import get_storage
storage = get_storage()
user_settings = storage.get_settings()
settings = get_settings()

if user_settings and hasattr(user_settings, 'ai_provider_primary'):
    primary = user_settings.ai_provider_primary
    fallback = user_settings.ai_provider_fallback if hasattr(user_settings, 'ai_provider_fallback') else None

    if fallback and fallback.lower() not in ['none', 'null', '']:
        st.sidebar.info(f"**AI:** {primary.capitalize()} → {fallback.capitalize()}")
    else:
        st.sidebar.info(f"**AI:** {primary.capitalize()}")
else:
    # Use env settings as fallback
    if settings.ai_service_primary == "ollama":
        st.sidebar.info("**AI:** Ollama")
    elif settings.ai_service_primary == "gemini":
        st.sidebar.info("**AI:** Gemini")

st.sidebar.markdown("---")
st.sidebar.caption("v1.0.0")

# Route to pages
if page == "Add Ideas":
    from src.ui import idea_entry
    idea_entry.show()

elif page == "Run Pipeline":
    from src.ui import pipeline_runner
    pipeline_runner.show()

elif page == "Review Content":
    from src.ui import content_review
    content_review.show()

elif page == "Analytics":
    from src.ui import analytics
    analytics.show()

elif page == "Settings":
    from src.ui import settings_page
    settings_page.show()
