"""Home page UI."""

import streamlit as st
from src.data.storage import get_storage


def show():
    """Display the home page."""

    st.markdown('<div class="main-header">LinkedIn Content Pipeline</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Automated content generation from your ideas</div>', unsafe_allow_html=True)

    # Quick stats
    storage = get_storage()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        ideas = storage.get_ideas()
        unused_ideas = storage.get_ideas(unused_only=True)
        st.metric("Total Ideas", len(ideas))
        st.caption(f"{len(unused_ideas)} unused")

    with col2:
        profiles = storage.get_profiles()
        st.metric("Brand Profiles", len(profiles))

    with col3:
        content = storage.get_content_list()
        st.metric("Generated Content", len(content))

    with col4:
        settings = storage.get_settings()
        if settings and settings.active_profile_id:
            active_profile = storage.get_profile(settings.active_profile_id)
            active_name = active_profile.profile_name if active_profile else "None"
        else:
            active_name = "None"
        st.metric("Active Profile", active_name)

    st.markdown("---")

    # How it works
    st.subheader("🎯 How It Works")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### Stage 1: Topic Curation
        📝 **Analyze your ideas**

        The pipeline reviews your collected ideas and identifies 5 compelling topics that resonate with your target audience.

        ➡️ Input: Your raw ideas
        ➡️ Output: Topic briefs
        """)

    with col2:
        st.markdown("""
        ### Stage 2: Content Development
        ✍️ **Write substantive content**

        Each topic is developed into 3 versions: Bridge (balanced), Aspirational (tactical), and Current (personal).

        ➡️ Input: Topic briefs
        ➡️ Output: Long-form content
        """)

    with col3:
        st.markdown("""
        ### Stage 3: Platform Optimization
        🎨 **Optimize for platforms**

        Content is adapted for LinkedIn and Twitter with proper formatting, hooks, hashtags, and engagement tactics.

        ➡️ Input: Developed content
        ➡️ Output: Ready-to-post content
        """)

    st.markdown("---")

    # Getting started
    st.subheader("🚀 Getting Started")

    settings = storage.get_settings()

    if not settings:
        st.warning("⚠️ **Setup Required**")
        st.markdown("""
        Get started in 3 steps:
        1. Go to **Settings** and configure your profile
        2. Add your first brand profile
        3. Go to **Add Ideas** and capture some content ideas
        4. Run the **Pipeline** to generate content
        """)

        if st.button("Go to Settings →", type="primary"):
            st.switch_page("pages/settings.py")

    else:
        ideas = storage.get_ideas(unused_only=True)

        if len(ideas) < 5:
            st.info(f"💡 **Add More Ideas**\n\nYou have {len(ideas)} unused ideas. Add at least 5 for best results.")

            if st.button("Add Ideas →", type="primary"):
                st.switch_page("pages/idea_entry.py")

        else:
            st.success("✅ **Ready to Generate Content!**")

            st.markdown(f"""
            You have:
            - ✅ {len(ideas)} unused ideas
            - ✅ {len(profiles)} brand profile(s)
            - ✅ Settings configured

            You're ready to run the pipeline!
            """)

            if st.button("Run Pipeline →", type="primary"):
                st.switch_page("pages/pipeline_runner.py")

    st.markdown("---")

    # Recent activity
    st.subheader("📋 Recent Activity")

    recent_content = storage.get_content_list(limit=5)

    if recent_content:
        for content in recent_content:
            with st.expander(f"Generated {content.generation_date.strftime('%Y-%m-%d %H:%M')} - {len(content.platform_posts)} posts"):
                st.write(f"**Profile:** {content.profile_id}")
                st.write(f"**Status:** {content.status.value}")
                st.write(f"**Topics:** {len(content.topic_briefs)}")
                st.write(f"**Content Pieces:** {len(content.developed_content)}")
                st.write(f"**Platform Posts:** {len(content.platform_posts)}")

                if st.button(f"View Details", key=content.generation_id):
                    st.session_state["selected_content"] = content.generation_id
                    st.switch_page("pages/content_review.py")
    else:
        st.info("No content generated yet. Run the pipeline to create your first content!")
