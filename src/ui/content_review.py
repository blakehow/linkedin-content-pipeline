"""Content review UI page."""

import streamlit as st
from src.data.storage import get_storage


def show():
    """Display the content review page."""

    st.title("📄 Review Generated Content")

    storage = get_storage()

    # Get content to review
    content_id = st.session_state.get("selected_content")

    if content_id:
        content = storage.get_content(content_id)

        if not content:
            st.error("Content not found")
            return

        # Header
        st.markdown(f"### Generated: {content.generation_date.strftime('%Y-%m-%d %H:%M')}")
        st.markdown(f"**Status:** {content.status.value} | **Profile:** {content.profile_id}")

        tabs = st.tabs([
            f"📝 Topics ({len(content.topic_briefs)})",
            f"✍️ Content ({len(content.developed_content)})",
            f"📱 Posts ({len(content.platform_posts)})"
        ])

        # Tab 1: Topics
        with tabs[0]:
            if content.topic_briefs:
                for i, topic in enumerate(content.topic_briefs, 1):
                    with st.expander(f"Topic {i}: {topic.core_insight[:50]}..."):
                        st.markdown(f"**Core Insight:** {topic.core_insight}")
                        st.markdown(f"**Audience Resonance:** {topic.audience_resonance}")
                        st.markdown(f"**Authentic Angle:** {topic.authentic_angle}")
                        st.markdown(f"**Potential Hook:** {topic.potential_hook}")
            else:
                st.info("No topics generated")

        # Tab 2: Developed Content
        with tabs[1]:
            if content.developed_content:
                for i, dev_content in enumerate(content.developed_content, 1):
                    with st.expander(f"{dev_content.version.value}: {dev_content.title}"):
                        st.markdown(f"### {dev_content.title}")
                        st.markdown(dev_content.body)

                        if dev_content.key_statistics:
                            st.markdown("**Key Statistics:**")
                            for stat in dev_content.key_statistics:
                                st.markdown(f"- {stat}")

                        st.caption(f"Word count: {dev_content.word_count} | Read time: {dev_content.estimated_read_time} min")
            else:
                st.info("No developed content")

        # Tab 3: Platform Posts
        with tabs[2]:
            if content.platform_posts:
                # Filter by platform
                linkedin_posts = [p for p in content.platform_posts if p.platform == "LinkedIn"]
                twitter_posts = [p for p in content.platform_posts if p.platform == "Twitter"]

                if linkedin_posts:
                    st.markdown("## LinkedIn Posts")
                    for i, post in enumerate(linkedin_posts, 1):
                        with st.expander(f"Variation {post.variation_number}: {post.hook_style}"):
                            st.text_area(
                                "Post Text",
                                value=post.text,
                                height=300,
                                key=f"linkedin-{post.post_id}"
                            )

                            if post.hashtags:
                                st.markdown(f"**Hashtags:** {' '.join(post.hashtags)}")

                            st.caption(f"Characters: {post.character_count}")

                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("📋 Copy to Clipboard", key=f"copy-ln-{post.post_id}"):
                                    st.code(post.text, language=None)
                            with col2:
                                if st.button("🔗 Open LinkedIn", key=f"open-ln-{post.post_id}"):
                                    st.markdown("[Open LinkedIn →](https://www.linkedin.com)")

                if twitter_posts:
                    st.markdown("## Twitter/X Threads")
                    for i, post in enumerate(twitter_posts, 1):
                        with st.expander(f"Thread {post.variation_number}: {post.hook_style}"):
                            if post.thread_parts:
                                for j, tweet in enumerate(post.thread_parts, 1):
                                    st.text_area(
                                        f"Tweet {j}",
                                        value=tweet,
                                        height=100,
                                        key=f"twitter-{post.post_id}-{j}"
                                    )
                            else:
                                st.text_area(
                                    "Thread Text",
                                    value=post.text,
                                    height=300,
                                    key=f"twitter-{post.post_id}"
                                )

                            if post.hashtags:
                                st.markdown(f"**Hashtags:** {' '.join(post.hashtags)}")

                            st.caption(f"Total characters: {post.character_count}")

                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("📋 Copy Thread", key=f"copy-tw-{post.post_id}"):
                                    st.code(post.text, language=None)
                            with col2:
                                if st.button("🔗 Open Twitter", key=f"open-tw-{post.post_id}"):
                                    st.markdown("[Open Twitter →](https://twitter.com)")
            else:
                st.info("No platform posts")

    else:
        # List all content
        st.markdown("Select content to review:")

        content_list = storage.get_content_list()

        if not content_list:
            st.info("No generated content yet. Run the pipeline first!")
        else:
            for content in content_list:
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

                with col1:
                    st.write(content.generation_date.strftime('%Y-%m-%d %H:%M'))
                with col2:
                    st.write(f"{len(content.topic_briefs)} topics")
                with col3:
                    st.write(f"{len(content.platform_posts)} posts")
                with col4:
                    if st.button("View", key=content.generation_id):
                        st.session_state["selected_content"] = content.generation_id
                        st.rerun()
