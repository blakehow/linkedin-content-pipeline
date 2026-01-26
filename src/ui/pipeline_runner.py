"""Pipeline runner UI page."""

import streamlit as st
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

    # Run pipeline button
    if st.button("🚀 Run Pipeline", type="primary", use_container_width=True):
        # Create progress containers
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(message: str, percent: float):
            """Update progress UI."""
            progress_bar.progress(min(100, int(percent)) / 100)
            status_text.text(message)

        try:
            # Run pipeline with selected ideas OR existing topics
            if mode == "🔄 Re-run from Existing Topics":
                result = orchestrator.run_full_pipeline(
                    profile_id=selected_profile_id,
                    existing_topics=selected_topics,
                    content_versions=content_versions,
                    platforms=platforms,
                    target_word_count=target_word_count,
                    progress_callback=update_progress
                )
            else:
                result = orchestrator.run_full_pipeline(
                    profile_id=selected_profile_id,
                    idea_ids=selected_idea_ids,
                    num_topics=num_topics,
                    content_versions=content_versions,
                    platforms=platforms,
                    target_word_count=target_word_count,
                    progress_callback=update_progress
                )

            # Success!
            st.success("✅ Pipeline completed successfully!")

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

            # Display Generated Content
            st.markdown("### 📝 Generated Content")

            # Show topics
            if result.topic_briefs:
                st.subheader("💡 Topics Generated")
                for i, topic in enumerate(result.topic_briefs, 1):
                    with st.expander(f"Topic {i}: {topic.core_insight[:60]}..."):
                        st.markdown(f"**Core Insight:** {topic.core_insight}")
                        st.markdown(f"**Audience Resonance:** {topic.audience_resonance}")
                        st.markdown(f"**Authentic Angle:** {topic.authentic_angle}")
                        st.markdown(f"**Hook:** {topic.potential_hook}")

            # Show developed content in 3 vertical containers
            if result.developed_content:
                st.subheader("✍️ Generated Content Versions")
                st.markdown("Review all 3 versions and choose which you like best:")

                # Group by topic and version
                for topic_idx, topic in enumerate(result.topic_briefs):
                    st.markdown(f"#### 💡 Topic {topic_idx + 1}: {topic.core_insight[:80]}...")

                    # Get all 3 versions for this topic
                    topic_contents = [c for c in result.developed_content if c.topic_id == topic.topic_id]

                    # Sort to ensure consistent order: Bridge, Aspirational, Current
                    version_order = {"Bridge Content": 1, "Aspirational Content": 2, "Current Content": 3}
                    topic_contents.sort(key=lambda x: version_order.get(x.version.value, 99))

                    for content in topic_contents:
                        version_emoji = {
                            "Bridge Content": "🌉",
                            "Aspirational Content": "🚀",
                            "Current Content": "💭"
                        }
                        emoji = version_emoji.get(content.version.value, "📄")

                        with st.container(border=True):
                            st.markdown(f"### {emoji} {content.version.value}")
                            st.markdown(f"**{content.title}**")
                            st.caption(f"📊 {content.word_count} words | ⏱️ ~{content.estimated_read_time} min read")

                            st.markdown("---")
                            st.text_area(
                                f"Content for {content.version.value}",
                                content.body,
                                height=400,
                                key=f"display-{content.content_id}",
                                label_visibility="collapsed"
                            )

                            # Edit and regenerate section
                            with st.expander("✏️ Edit & Regenerate"):
                                edit_prompt = st.text_area(
                                    "Suggest edits or changes",
                                    placeholder="e.g., 'Make it more data-driven' or 'Add a personal story about leadership' or 'Shorten to 800 words'",
                                    height=80,
                                    key=f"edit-{content.content_id}"
                                )

                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("🔄 Regenerate", key=f"regen-{content.content_id}", use_container_width=True, type="primary"):
                                        if not edit_prompt.strip():
                                            st.error("Please provide edit instructions before regenerating.")
                                        else:
                                            with st.spinner("Regenerating content with your edits..."):
                                                try:
                                                    ai_client = create_ai_client()

                                                    regenerate_prompt = f"""You are revising this content based on user feedback.

Original Content:
{content.body}

User's Edit Instructions:
{edit_prompt}

Please rewrite the content incorporating the user's requested changes while maintaining the overall structure and quality. Keep the same content version style ({content.version.value}).

Output only the revised content, no explanations."""

                                                    regenerated = ai_client.generate(regenerate_prompt, max_tokens=3000)

                                                    # Update content in session state for display
                                                    st.session_state[f"regenerated_{content.content_id}"] = regenerated
                                                    st.success("✅ Content regenerated! See below:")
                                                    st.rerun()

                                                except Exception as e:
                                                    st.error(f"❌ Regeneration failed: {str(e)}")
                                                    st.info("The original content is still available above.")

                                with col2:
                                    if st.button("📋 Copy", key=f"copy-{content.content_id}", use_container_width=True):
                                        st.code(content.body, language="text")

                            # LinkedIn URL tracking
                            st.markdown("---")
                            st.markdown("##### 🔗 Track Published Post")

                            # Check if this content has corresponding platform posts
                            content_posts = [p for p in result.platform_posts if p.content_id == content.content_id]

                            if content_posts:
                                for post in content_posts:
                                    if post.platform == "linkedin":
                                        col1, col2 = st.columns([3, 1])

                                        with col1:
                                            # Show existing URL if saved
                                            if hasattr(post, 'linkedin_url') and post.linkedin_url:
                                                st.success(f"✅ Published: {post.linkedin_url}")
                                                if hasattr(post, 'published_at') and post.published_at:
                                                    st.caption(f"Published on: {post.published_at.strftime('%Y-%m-%d %H:%M')}")
                                            else:
                                                linkedin_url_input = st.text_input(
                                                    "LinkedIn Post URL",
                                                    placeholder="https://www.linkedin.com/posts/...",
                                                    key=f"url-{post.post_id}",
                                                    label_visibility="collapsed"
                                                )

                                        with col2:
                                            if not (hasattr(post, 'linkedin_url') and post.linkedin_url):
                                                if st.button("💾 Save", key=f"save-url-{post.post_id}", use_container_width=True):
                                                    url_key = f"url-{post.post_id}"
                                                    if url_key in st.session_state and st.session_state[url_key]:
                                                        from datetime import datetime
                                                        post.linkedin_url = st.session_state[url_key]
                                                        post.published_at = datetime.now()
                                                        storage.update_content(result)
                                                        st.success("URL saved!")
                                                        st.rerun()
                                                    else:
                                                        st.error("Please enter a URL")
                            else:
                                st.caption("💡 Platform posts will appear here after generation completes")

                            # Show regenerated version if it exists
                            if f"regenerated_{content.content_id}" in st.session_state:
                                st.markdown("---")
                                st.markdown("### ✨ Regenerated Version")
                                regenerated_content = st.session_state[f"regenerated_{content.content_id}"]
                                st.text_area(
                                    "Regenerated content",
                                    regenerated_content,
                                    height=400,
                                    key=f"regen-display-{content.content_id}",
                                    label_visibility="collapsed"
                                )

                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    if st.button("✅ Use This", key=f"use-regen-{content.content_id}", use_container_width=True):
                                        # Update the content object
                                        content.body = regenerated_content
                                        content.word_count = len(regenerated_content.split())
                                        storage.update_content(result)
                                        del st.session_state[f"regenerated_{content.content_id}"]
                                        st.success("Content updated!")
                                        st.rerun()

                                with col2:
                                    if st.button("📋 Copy", key=f"copy-regen-{content.content_id}", use_container_width=True):
                                        st.code(regenerated_content, language="text")

                                with col3:
                                    if st.button("❌ Discard", key=f"discard-regen-{content.content_id}", use_container_width=True):
                                        del st.session_state[f"regenerated_{content.content_id}"]
                                        st.rerun()

                    st.markdown("---")  # Separator between topics

            # Show platform posts
            if result.platform_posts:
                st.subheader("🎨 Platform Posts")

                # Group by platform
                linkedin_posts = [p for p in result.platform_posts if p.platform == "linkedin"]
                twitter_posts = [p for p in result.platform_posts if p.platform == "twitter"]

                col_left, col_right = st.columns(2)

                with col_left:
                    if linkedin_posts:
                        st.markdown("**📘 LinkedIn Posts**")
                        for i, post in enumerate(linkedin_posts, 1):
                            with st.container():
                                st.markdown(f"**Post {i}**")
                                st.text_area("", post.content, height=250, key=f"linkedin-{i}", disabled=True)
                                if st.button("📋 Copy", key=f"copy-li-{i}"):
                                    st.code(post.content)
                                st.markdown("---")

                with col_right:
                    st.markdown("**📤 Post Actions**")
                    st.info("Select posts to publish to LinkedIn:")

                    for i, post in enumerate(linkedin_posts, 1):
                        if st.checkbox(f"Post {i}", key=f"select-post-{i}"):
                            st.session_state[f"selected_post_{i}"] = post.content

                    st.markdown("---")

                    if st.button("📤 Publish Selected to LinkedIn", type="primary"):
                        selected_posts = [
                            st.session_state.get(f"selected_post_{i}")
                            for i in range(1, len(linkedin_posts) + 1)
                            if st.session_state.get(f"selected_post_{i}")
                        ]

                        if selected_posts:
                            st.warning("⚠️ Auto-posting to LinkedIn requires LinkedIn API credentials")
                            st.markdown("**To enable auto-posting:**")
                            st.markdown("1. Add LinkedIn API credentials in Settings")
                            st.markdown("2. Or manually copy/paste posts (recommended)")

                            with st.expander("📋 Copy Posts for Manual Posting"):
                                for i, content in enumerate(selected_posts, 1):
                                    st.markdown(f"**Post {i}:**")
                                    st.code(content)
                        else:
                            st.warning("Please select at least one post")

            st.markdown("---")

            st.info("💡 **Tip:** You can also view this content later in the **📄 Review Content** page")

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

                # Removed page switch button - use sidebar navigation instead
    else:
        st.info("No pipeline runs yet. Run your first pipeline above!")
