"""Pipeline runner UI page."""

import streamlit as st
from src.data.storage import get_storage
from src.pipeline.orchestrator import PipelineOrchestrator


def show():
    """Display the pipeline runner page."""

    st.title("🚀 Run Content Pipeline")
    st.markdown("Generate content from your ideas through the 3-stage pipeline.")

    storage = get_storage()
    orchestrator = PipelineOrchestrator()

    # Check prerequisites
    settings = storage.get_settings()
    if not settings:
        st.error("⚠️ Please configure your settings first.")
        if st.button("Go to Settings"):
            st.switch_page("pages/settings.py")
        return

    profiles = storage.get_profiles()
    if not profiles:
        st.error("⚠️ Please create at least one brand profile.")
        if st.button("Go to Settings"):
            st.switch_page("pages/settings.py")
        return

    ideas = storage.get_ideas(unused_only=True)
    if len(ideas) < 5:
        st.warning(f"⚠️ You have {len(ideas)} unused ideas. At least 5 recommended for best results.")

    # Pipeline configuration
    st.subheader("Pipeline Configuration")

    col1, col2 = st.columns(2)

    with col1:
        # Profile selection
        profile_names = {p.profile_id: p.profile_name for p in profiles}
        default_profile = settings.active_profile_id if settings.active_profile_id in profile_names else list(profile_names.keys())[0]

        selected_profile_id = st.selectbox(
            "Brand Profile",
            options=list(profile_names.keys()),
            format_func=lambda x: profile_names[x],
            index=list(profile_names.keys()).index(default_profile) if default_profile in profile_names else 0
        )

        # Show profile details
        selected_profile = storage.get_profile(selected_profile_id)
        if selected_profile:
            st.caption(f"**Audience:** {selected_profile.target_audience}")
            st.caption(f"**Tone:** {selected_profile.tone}")

    with col2:
        num_ideas = st.number_input(
            "Number of Ideas to Use",
            min_value=5,
            max_value=min(50, len(ideas)),
            value=min(10, len(ideas)),
            help="How many unused ideas to analyze"
        )

        num_topics = st.number_input(
            "Number of Topics to Generate",
            min_value=1,
            max_value=10,
            value=5,
            help="How many topic briefs to curate"
        )

    # Content version selection
    st.markdown("**Content Versions to Generate:**")
    col1, col2, col3 = st.columns(3)

    with col1:
        gen_bridge = st.checkbox("Bridge Content", value=True, help="Balanced: personal + tactical")
    with col2:
        gen_aspirational = st.checkbox("Aspirational Content", value=False, help="High-level, framework-heavy")
    with col3:
        gen_current = st.checkbox("Current Content", value=False, help="Personal, vulnerable")

    content_versions = []
    if gen_bridge:
        content_versions.append("bridge")
    if gen_aspirational:
        content_versions.append("aspirational")
    if gen_current:
        content_versions.append("current")

    if not content_versions:
        st.error("Please select at least one content version")
        return

    # Platform selection
    st.markdown("**Platforms to Optimize For:**")
    col1, col2 = st.columns(2)

    with col1:
        gen_linkedin = st.checkbox("LinkedIn", value=True)
    with col2:
        gen_twitter = st.checkbox("Twitter/X", value=True)

    platforms = []
    if gen_linkedin:
        platforms.append("linkedin")
    if gen_twitter:
        platforms.append("twitter")

    if not platforms:
        st.error("Please select at least one platform")
        return

    st.markdown("---")

    # Run pipeline button
    if st.button("🚀 Run Pipeline", type="primary", use_container_width=True):
        if len(ideas) < num_ideas:
            st.error(f"Not enough unused ideas. You have {len(ideas)}, but requested {num_ideas}.")
            return

        # Create progress containers
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(message: str, percent: float):
            """Update progress UI."""
            progress_bar.progress(min(100, int(percent)) / 100)
            status_text.text(message)

        try:
            # Run pipeline
            result = orchestrator.run_full_pipeline(
                profile_id=selected_profile_id,
                num_ideas=num_ideas,
                num_topics=num_topics,
                content_versions=content_versions,
                platforms=platforms,
                progress_callback=update_progress
            )

            # Success!
            st.success("✅ Pipeline completed successfully!")
            st.balloons()

            # Show summary
            st.markdown("### 📊 Generation Summary")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Ideas Used", len(result.source_idea_ids))
            with col2:
                st.metric("Topics Generated", len(result.topic_briefs))
            with col3:
                st.metric("Content Pieces", len(result.developed_content))
            with col4:
                st.metric("Platform Posts", len(result.platform_posts))

            # Store result in session state for review
            st.session_state["latest_generation"] = result.generation_id

            st.markdown("---")

            if st.button("📄 Review Generated Content →", type="primary"):
                st.session_state["selected_content"] = result.generation_id
                st.switch_page("pages/content_review.py")

        except Exception as e:
            st.error(f"❌ Pipeline failed: {str(e)}")
            st.exception(e)

    # Recent runs
    st.markdown("---")
    st.subheader("📋 Recent Pipeline Runs")

    recent = storage.get_content_list(limit=5)

    if recent:
        for content in recent:
            with st.expander(f"{content.generation_date.strftime('%Y-%m-%d %H:%M')} - {len(content.platform_posts)} posts"):
                st.write(f"**Status:** {content.status.value}")
                st.write(f"**Profile:** {content.profile_id}")
                st.write(f"**Topics:** {len(content.topic_briefs)}")
                st.write(f"**Content:** {len(content.developed_content)}")
                st.write(f"**Posts:** {len(content.platform_posts)}")

                if st.button("View", key=f"view-{content.generation_id}"):
                    st.session_state["selected_content"] = content.generation_id
                    st.switch_page("pages/content_review.py")
    else:
        st.info("No pipeline runs yet. Run your first pipeline above!")
