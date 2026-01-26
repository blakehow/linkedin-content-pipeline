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

# Custom CSS - Professional Theme with High Contrast
st.markdown("""
    <style>
    /* Main content area */
    .stApp {
        font-size: 0.95rem;
    }

    /* Headers - clear and readable */
    h1 {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
    }

    h2 {
        font-size: 1.4rem !important;
        font-weight: 500 !important;
    }

    h3 {
        font-size: 1.15rem !important;
        font-weight: 500 !important;
    }

    /* Ensure all text is readable */
    p, span, div, label {
        color: inherit !important;
    }

    /* Text areas and inputs - high contrast */
    .stTextArea textarea, .stTextInput input, .stSelectbox select {
        font-size: 0.95rem !important;
        padding: 0.5rem !important;
    }

    /* Buttons */
    .stButton button {
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        border-radius: 4px !important;
        padding: 0.5rem 1rem !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-size: 0.95rem !important;
    }

    /* Reduce spacing */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
    }

    /* Info/Warning/Error boxes - ensure visibility */
    .stAlert {
        padding: 1rem !important;
    }

    /* Metric values */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
    }

    /* Captions */
    .stCaptionContainer {
        font-size: 0.85rem !important;
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
