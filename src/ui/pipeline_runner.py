"""Pipeline runner UI page."""

import streamlit as st
import time
from src.data.storage import get_storage
from src.pipeline.orchestrator import PipelineOrchestrator
from src.ai.factory import create_ai_client


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
        st.info("👈 Use the sidebar to navigate to **⚙️ Settings**")
        return

    profiles = storage.get_profiles()
    if not profiles:
        st.error("⚠️ Please create at least one brand profile.")
        st.info("👈 Use the sidebar to navigate to **⚙️ Settings**")
        return

    # Get categories from settings
    categories = settings.idea_categories if settings and hasattr(settings, 'idea_categories') else [
        "General", "Leadership", "Team Management", "Product Development",
        "Personal Growth", "AI & Technology", "Marketing", "Operations",
        "Customer Success", "Other"
    ]

    # Mode selection: New ideas or existing topics
    st.subheader("🎯 Content Source")

    mode = st.radio(
        "Choose content source:",
        ["📝 Generate from New Ideas", "🔄 Re-run from Existing Topics"],
        horizontal=True,
        help="Generate new topics from your ideas, or regenerate content from previously created topics"
    )

    st.markdown("---")

    if mode == "🔄 Re-run from Existing Topics":
        # Show existing topics from previous pipeline runs
        st.subheader("📚 Select Existing Topics")

        # Get all previous generations that have topics
        all_content = storage.get_content_list(limit=50)

        # Extract all unique topics
        all_topics = []
        topic_to_gen = {}  # Map topic_id to generation_id

        for content in all_content:
            if content.topic_briefs:
                for topic in content.topic_briefs:
                    if topic.topic_id not in topic_to_gen:
                        all_topics.append(topic)
                        topic_to_gen[topic.topic_id] = content.generation_id

        if not all_topics:
            st.warning("⚠️ No existing topics found.")
            st.info("""
            **How to create topics:**
            1. Switch to "📝 Generate from New Ideas" mode above
            2. Select some ideas
            3. Run the pipeline
            4. Come back here to re-run those topics later!

            *Note: "Used ideas" in the Add Ideas screen just means ideas were consumed by a pipeline run. You need to generate content first before topics appear here.*
            """)
            return

        st.info(f"📊 Found {len(all_topics)} topics from previous runs. Select which ones to regenerate content for.")

        # Display topics with checkboxes
        selected_topic_ids = []

        for i, topic in enumerate(all_topics):
            # Format display
            date_generated = all_content[0].generation_date.strftime('%Y-%m-%d') if all_content else ""

            if st.checkbox(
                f"**{topic.core_insight[:100]}...**",
                key=f"topic-select-{topic.topic_id}"
            ):
                selected_topic_ids.append(topic.topic_id)

            # Show preview in expander
            with st.expander(f"Preview Topic {i+1}"):
                st.markdown(f"**Core Insight:** {topic.core_insight}")
                st.markdown(f"**Audience Resonance:** {topic.audience_resonance}")
                st.markdown(f"**Authentic Angle:** {topic.authentic_angle}")
                st.markdown(f"**Hook:** {topic.potential_hook}")
                st.caption(f"Generated: {date_generated} | Source: {topic_to_gen.get(topic.topic_id, 'Unknown')}")

        if not selected_topic_ids:
            st.info("✅ Select at least one topic above to continue")
            return

        st.success(f"✅ {len(selected_topic_ids)} topics selected for regeneration")

        # Store selected topics for pipeline
        selected_topics = [t for t in all_topics if t.topic_id in selected_topic_ids]
        selected_idea_ids = None  # No ideas needed for existing topics

    else:
        # Category-based idea selection (original flow)
        st.subheader("📂 Select Ideas")

        selected_categories = st.multiselect(
            "Filter by Categories",
            options=categories,
            default=categories,
            help="Choose which categories to show"
        )

        # Get filtered ideas
        all_ideas = storage.get_ideas(unused_only=True)
        filtered_ideas = [
            idea for idea in all_ideas
            if idea.category in selected_categories
        ]

        if not filtered_ideas:
            st.warning("⚠️ No unused ideas in selected categories. Please add ideas or select different categories.")
            return

        st.markdown(f"**{len(filtered_ideas)} unused ideas available:**")

        # Checkbox selection
        selected_idea_ids = []
        for idea in filtered_ideas:
            # Use title if available, otherwise show truncated text
            display_title = idea.title if hasattr(idea, 'title') and idea.title else idea.text[:60] + "..."

            if st.checkbox(
                f"{display_title} ({idea.category})",
                key=f"idea-{idea.id}"
            ):
                selected_idea_ids.append(idea.id)

        if not selected_idea_ids:
            st.info("✅ Select at least one idea using the checkboxes above to continue")
            return

        st.success(f"✅ {len(selected_idea_ids)} ideas selected")
        selected_topics = None  # Will generate new topics from ideas

    st.markdown("---")

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
        if mode == "🔄 Re-run from Existing Topics":
            st.info(f"Using {len(selected_topics)} existing topics")
            num_topics = len(selected_topics)
        else:
            num_topics = st.number_input(
                "Number of Topics to Generate",
                min_value=1,
                max_value=min(10, len(selected_idea_ids)),
                value=min(3, len(selected_idea_ids)),
                help="How many topic briefs to curate from selected ideas"
            )

    # Article length/words/time selection
    st.markdown("**Content Length:**")

    # Choose input method
    length_method = st.radio(
        "Specify by:",
        ["Preset Length", "Target Words", "Read Time"],
        horizontal=True,
        help="Choose how to define the article length"
    )

    col1, col2, col3 = st.columns(3)

    if length_method == "Preset Length":
        with col1:
            length_option = st.selectbox(
                "Length",
                ["Short", "Medium", "Long"],
                index=1
            )

            # Map to word count
            length_map = {
                "Short": 600,
                "Medium": 1200,
                "Long": 2000
            }
            target_word_count = length_map[length_option]

        with col2:
            st.metric("Target Words", f"{target_word_count}")

        with col3:
            st.metric("Read Time", f"~{target_word_count // 200} min")

    elif length_method == "Target Words":
        with col1:
            target_word_count = st.number_input(
                "Target Word Count",
                min_value=300,
                max_value=5000,
                value=1200,
                step=100,
                help="Specify exact word count target"
            )

        with col2:
            st.metric("Read Time", f"~{target_word_count // 200} min")

        with col3:
            # Show approximate length category
            if target_word_count < 800:
                st.caption("📝 Short")
            elif target_word_count < 1600:
                st.caption("📄 Medium")
            else:
                st.caption("📚 Long")

    else:  # Read Time
        with col1:
            read_time = st.number_input(
                "Target Read Time (minutes)",
                min_value=1,
                max_value=25,
                value=6,
                step=1,
                help="Average reading speed: 200 words/minute"
            )

            # Convert to word count (200 words per minute)
            target_word_count = read_time * 200

        with col2:
            st.metric("Target Words", f"~{target_word_count}")

        with col3:
            # Show approximate length category
            if target_word_count < 800:
                st.caption("📝 Short")
            elif target_word_count < 1600:
                st.caption("📄 Medium")
            else:
                st.caption("📚 Long")

    # Always generate all 3 versions (no UI needed)
    content_versions = ["bridge", "aspirational", "current"]

    # Platform selection (LinkedIn only now)
    st.markdown("**Platform:**")
    st.info("📘 LinkedIn content generation enabled")

    platforms = ["linkedin"]

    st.markdown("---")

    # Show estimated runtime
    if mode == "🔄 Re-run from Existing Topics":
        num_topics_est = len(selected_topics) if selected_topics else 0
    else:
        num_topics_est = num_topics

    if num_topics_est > 0:
        ai_provider = settings.ai_provider_primary if settings and hasattr(settings, 'ai_provider_primary') else None

        estimated_seconds, est_stats = orchestrator.get_estimated_runtime(
            num_topics=num_topics_est,
            num_versions=3,
            ai_provider=ai_provider
        )

        if estimated_seconds < 60:
            est_display = f"{int(estimated_seconds)}s"
        else:
            est_minutes = estimated_seconds / 60
            est_display = f"{est_minutes:.1f} min"

        confidence_icons = {"high": "✓", "medium": "~", "low": "?"}
        confidence_icon = confidence_icons.get(est_stats.get("confidence", "low"), "?")

        st.info(f"**Estimated wait time:** {est_display} {confidence_icon}")
        if est_stats.get("source") == "default_estimates":
            st.caption("Based on default estimates (no historical data yet)")
        else:
            st.caption(f"Based on {est_stats['sample_size']} recent runs")

    # Run pipeline button
    if st.button("Run Pipeline", type="primary", use_container_width=True):
        # Create progress containers
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(message: str, percent: float):
            """Update progress UI."""
            progress_bar.progress(min(100, int(percent)) / 100)
            status_text.text(message)

        # Track start time
        start_time = time.time()

        # Containers for progressive display
        topics_container = st.empty()
        st.markdown("---")
        st.markdown("### Generated Content")
        content_display_area = st.container()

        try:
            # Run pipeline progressively with selected ideas OR existing topics
            pipeline_params = {
                "profile_id": selected_profile_id,
                "content_versions": content_versions,
                "platforms": platforms,
                "target_word_count": target_word_count,
                "progress_callback": update_progress
            }

            if mode == "🔄 Re-run from Existing Topics":
                pipeline_params["existing_topics"] = selected_topics
            else:
                pipeline_params["idea_ids"] = selected_idea_ids
                pipeline_params["num_topics"] = num_topics

            pipeline_generator = orchestrator.run_pipeline_progressive(**pipeline_params)

            topic_briefs = []
            # Store content by topic and version for side-by-side display
            content_by_topic = {}  # {topic_id: {version_name: content}}
            final_result = None

            # Process results as they're yielded
            for stage_type, data in pipeline_generator:
                if stage_type == "topics":
                    topic_briefs = data
                    with topics_container.container():
                        st.markdown("### Topics Generated")
                        for i, topic in enumerate(topic_briefs, 1):
                            with st.expander(f"Topic {i}: {topic.core_insight[:60]}...", expanded=False):
                                st.markdown(f"**Core Insight:** {topic.core_insight}")
                                st.markdown(f"**Audience Resonance:** {topic.audience_resonance}")
                                st.markdown(f"**Authentic Angle:** {topic.authentic_angle}")

                    # Initialize content storage for each topic
                    for topic in topic_briefs:
                        content_by_topic[topic.topic_id] = {}

                elif stage_type == "content":
                    content = data

                    # Map from enum value to custom name from settings
                    version_map = {
                        "Bridge Content": settings.content_version_names[0] if hasattr(settings, 'content_version_names') and len(settings.content_version_names) > 0 else "Bridge",
                        "Aspirational Content": settings.content_version_names[1] if hasattr(settings, 'content_version_names') and len(settings.content_version_names) > 1 else "Aspirational",
                        "Current Content": settings.content_version_names[2] if hasattr(settings, 'content_version_names') and len(settings.content_version_names) > 2 else "Current"
                    }
                    version_name = version_map.get(content.version.value, content.version.value)

                    # Store content by topic and version
                    if content.topic_id not in content_by_topic:
                        content_by_topic[content.topic_id] = {}
                    content_by_topic[content.topic_id][version_name] = content

                    # Don't re-render entire area - we'll show final results at the end

                elif stage_type == "complete":
                    final_result = data

            # Now display all content side-by-side after pipeline completes
            if content_by_topic:
                with content_display_area:
                    for topic_idx, topic in enumerate(topic_briefs):
                        st.markdown(f"### Topic {topic_idx + 1}: {topic.core_insight[:80]}...")

                        # Create 3 columns for side-by-side comparison
                        col1, col2, col3 = st.columns(3)

                        # Get custom version names
                        version_names = [
                            settings.content_version_names[0] if hasattr(settings, 'content_version_names') and len(settings.content_version_names) > 0 else "Bridge",
                            settings.content_version_names[1] if hasattr(settings, 'content_version_names') and len(settings.content_version_names) > 1 else "Aspirational",
                            settings.content_version_names[2] if hasattr(settings, 'content_version_names') and len(settings.content_version_names) > 2 else "Current"
                        ]

                        cols = [col1, col2, col3]

                        for idx, (col, vname) in enumerate(zip(cols, version_names)):
                            with col:
                                st.markdown(f"**{vname}**")

                                if topic.topic_id in content_by_topic and vname in content_by_topic[topic.topic_id]:
                                    c = content_by_topic[topic.topic_id][vname]
                                    st.caption(f"{c.word_count} words | {c.estimated_read_time} min")
                                    if hasattr(c, '_generation_time'):
                                        st.caption(f"⏱️ {c._generation_time:.1f}s")

                                    st.markdown(f"**{c.title}**")
                                    st.text_area(
                                        f"{vname} content",
                                        c.body,
                                        height=500,
                                        key=f"side-{topic.topic_id}-{vname}",
                                        label_visibility="collapsed"
                                    )
                                else:
                                    st.info("Content not generated")

                        st.markdown("---")

            elapsed_time = time.time() - start_time

            # Final summary with timing
            st.success(f"Pipeline completed in {elapsed_time:.1f}s")

            if final_result:
                # Show summary
                st.markdown("### Generation Summary")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Ideas Used", len(final_result.source_idea_ids))
                with col2:
                    st.metric("Topics Generated", len(final_result.topic_briefs))
                with col3:
                    st.metric("Content Pieces", len(final_result.developed_content))
                with col4:
                    st.metric("Total Time", f"{elapsed_time:.1f}s")

                # Show timing breakdown if available
                if hasattr(final_result, 'stage1_duration_seconds') and final_result.stage1_duration_seconds:
                    st.caption(f"**Timing:** Stage 1: {final_result.stage1_duration_seconds:.1f}s | Stage 2+3: {final_result.stage2_duration_seconds + final_result.stage3_duration_seconds:.1f}s | Provider: {final_result.ai_provider_used}")

                # Store result in session state for review
                st.session_state["latest_generation"] = final_result.generation_id

        except Exception as e:
            st.error(f"Pipeline failed: {str(e)}")
            st.exception(e)

    # Recent runs
    st.markdown("---")
    st.subheader("Recent Pipeline Runs")

    recent = storage.get_content_list(limit=5)

    if recent:
        for content in recent:
            with st.expander(f"{content.generation_date.strftime('%Y-%m-%d %H:%M')} - {len(content.platform_posts)} posts"):
                st.write(f"**Status:** {content.status.value}")
                st.write(f"**Profile:** {content.profile_id}")
                st.write(f"**Topics:** {len(content.topic_briefs)}")
                st.write(f"**Content:** {len(content.developed_content)}")
                st.write(f"**Posts:** {len(content.platform_posts)}")

                # Show timing if available
                if hasattr(content, 'pipeline_duration_seconds') and content.pipeline_duration_seconds:
                    st.write(f"**Duration:** {content.pipeline_duration_seconds:.1f}s")
                    if hasattr(content, 'ai_provider_used') and content.ai_provider_used:
                        st.write(f"**AI Provider:** {content.ai_provider_used}")
    else:
        st.info("No pipeline runs yet. Run your first pipeline above!")
