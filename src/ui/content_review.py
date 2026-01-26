"""Content review and management UI page."""

import streamlit as st
from src.data.storage import get_storage


def show():
    """Display the content review and management page."""

    st.title("📄 Content Management")

    storage = get_storage()

    # Check if content is selected and auto-switch to Selected Item view
    selected_content_id = st.session_state.get("selected_content")

    # Sidebar filters
    with st.sidebar:
        st.markdown("### Filters")

        # Auto-switch to Selected Item if content was selected
        if selected_content_id and "view_mode" not in st.session_state:
            default_view = "Selected Item"
        else:
            default_view = st.session_state.get("view_mode", "All Content")

        view_mode = st.radio(
            "View Mode",
            ["All Content", "Selected Item"],
            index=0 if default_view == "All Content" else 1
        )

        # Save view mode to session state
        st.session_state["view_mode"] = view_mode

    content_list = storage.get_content_list()

    if not content_list:
        st.info("📝 No generated content yet. Run the pipeline first!")
        return

    if view_mode == "All Content":
        show_content_list(storage, content_list)
    else:
        show_selected_content(storage)


def show_content_list(storage, content_list):
    """Show list of all content with management options."""

    st.markdown("### 📚 All Generated Content")
    st.markdown(f"**Total:** {len(content_list)} content generations")

    # Bulk actions
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("---")
    with col2:
        if st.button("🗑️ Delete All", type="secondary"):
            if st.session_state.get("confirm_delete_all"):
                for content in content_list:
                    storage.delete_content(content.generation_id)
                st.success("✅ All content deleted!")
                st.rerun()
            else:
                st.session_state["confirm_delete_all"] = True
                st.warning("⚠️ Click again to confirm")

    # Display each content item
    for content in content_list:
        with st.expander(
            f"🗓️ {content.generation_date.strftime('%Y-%m-%d %H:%M')} | "
            f"{len(content.topic_briefs)} topics | {len(content.platform_posts)} posts",
            expanded=False
        ):
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                st.markdown(f"**Profile:** {content.profile_id}")
                st.markdown(f"**Status:** {content.status.value}")
                st.markdown(f"**ID:** `{content.generation_id[:8]}...`")

            with col2:
                st.markdown(f"**Topics:** {len(content.topic_briefs)}")
                st.markdown(f"**Content Pieces:** {len(content.developed_content)}")
                st.markdown(f"**Platform Posts:** {len(content.platform_posts)}")

            with col3:
                if st.button("👁️ View", key=f"view-{content.generation_id}"):
                    st.session_state["selected_content"] = content.generation_id
                    st.session_state["view_mode"] = "Selected Item"
                    st.rerun()

            # Action buttons
            st.markdown("---")
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("📥 Export", key=f"export-{content.generation_id}"):
                    export_content(content)

            with col2:
                if st.button("📋 Copy All Posts", key=f"copy-{content.generation_id}"):
                    show_all_posts_for_copy(content)

            with col3:
                if st.button("🗑️ Delete", key=f"delete-{content.generation_id}", type="secondary"):
                    if storage.delete_content(content.generation_id):
                        st.success("✅ Content deleted!")
                        st.rerun()


def show_selected_content(storage):
    """Show detailed view of selected content."""

    content_id = st.session_state.get("selected_content")

    if not content_id:
        st.info("👈 Select content from the sidebar to view details")
        return

    content = storage.get_content(content_id)

    if not content:
        st.error("❌ Content not found")
        st.session_state["selected_content"] = None
        return

    # Header with actions
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

    with col1:
        st.markdown(f"### 📅 {content.generation_date.strftime('%Y-%m-%d %H:%M')}")

    with col2:
        if st.button("📥 Export"):
            export_content(content)

    with col3:
        if st.button("📋 Copy All"):
            show_all_posts_for_copy(content)

    with col4:
        if st.button("🗑️ Delete", type="secondary"):
            if storage.delete_content(content_id):
                st.success("✅ Deleted!")
                st.session_state["selected_content"] = None
                st.session_state["view_mode"] = "All Content"
                st.rerun()

    # Back button
    st.markdown("---")
    if st.button("⬅️ Back to All Content"):
        st.session_state["view_mode"] = "All Content"
        st.session_state["selected_content"] = None
        st.rerun()

    st.markdown(f"**Status:** {content.status.value} | **Profile:** {content.profile_id}")

    # Tabs for different content types
    tabs = st.tabs([
        f"💡 Topics ({len(content.topic_briefs)})",
        f"✍️ Content ({len(content.developed_content)})",
        f"📱 Posts ({len(content.platform_posts)})"
    ])

    # Tab 1: Topics
    with tabs[0]:
        if content.topic_briefs:
            for i, topic in enumerate(content.topic_briefs, 1):
                with st.expander(f"Topic {i}: {topic.core_insight[:60]}...", expanded=True):
                    st.markdown(f"**Core Insight:** {topic.core_insight}")
                    st.markdown(f"**Audience Resonance:** {topic.audience_resonance}")
                    st.markdown(f"**Authentic Angle:** {topic.authentic_angle}")
                    st.markdown(f"**Hook:** {topic.potential_hook}")
        else:
            st.info("No topics generated")

    # Tab 2: Developed Content
    with tabs[1]:
        if content.developed_content:
            for i, dev_content in enumerate(content.developed_content, 1):
                with st.expander(f"Content {i}: {dev_content.title}", expanded=True):
                    st.markdown(f"**Type:** {dev_content.version.value}")
                    st.text_area("Full Content", dev_content.body, height=300, key=f"content-{i}")

                    if st.button(f"📋 Copy Content {i}", key=f"copy-content-{i}"):
                        st.code(dev_content.body)
        else:
            st.info("No developed content")

    # Tab 3: Platform Posts
    with tabs[2]:
        if content.platform_posts:
            linkedin_posts = [p for p in content.platform_posts if p.platform == "linkedin"]

            if linkedin_posts:
                st.markdown("### 📘 LinkedIn Posts")

                # Post selection for publishing
                st.markdown("**Select posts to publish:**")
                selected_for_publish = []

                for i, post in enumerate(linkedin_posts, 1):
                    with st.container(border=True):
                        st.markdown(f"**Post {i}**")

                        # Show LinkedIn URL if saved
                        if hasattr(post, 'linkedin_url') and post.linkedin_url:
                            st.success(f"🔗 Published: [{post.linkedin_url}]({post.linkedin_url})")
                            if hasattr(post, 'published_at') and post.published_at:
                                st.caption(f"Published on: {post.published_at.strftime('%Y-%m-%d %H:%M')}")

                        st.text_area("Content", post.content, height=200, key=f"review-li-{i}", disabled=True, label_visibility="collapsed")

                        col1, col2 = st.columns(2)

                        with col1:
                            if st.button("📋 Copy", key=f"copy-review-li-{i}", use_container_width=True):
                                st.code(post.content)

                        with col2:
                            if st.checkbox("Select for publish", key=f"select-review-{i}"):
                                selected_for_publish.append((i, post.content))

                        # LinkedIn URL input (if not already saved)
                        if not (hasattr(post, 'linkedin_url') and post.linkedin_url):
                            st.markdown("---")
                            st.markdown("**🔗 Add LinkedIn URL:**")

                            col1, col2 = st.columns([3, 1])

                            with col1:
                                linkedin_url = st.text_input(
                                    "LinkedIn Post URL",
                                    placeholder="https://www.linkedin.com/posts/...",
                                    key=f"url-input-{post.post_id}",
                                    label_visibility="collapsed"
                                )

                            with col2:
                                if st.button("💾 Save URL", key=f"save-url-{post.post_id}", use_container_width=True):
                                    if linkedin_url:
                                        from datetime import datetime as dt
                                        post.linkedin_url = linkedin_url
                                        post.published_at = dt.now()
                                        storage.update_content(content)
                                        st.success("✅ URL saved!")
                                        st.rerun()
                                    else:
                                        st.error("Please enter a URL")

                # Publish button
                if selected_for_publish:
                    st.markdown("### 📤 Publish to LinkedIn")

                    if st.button("📤 Publish Selected Posts", type="primary"):
                        st.warning("⚠️ LinkedIn auto-posting requires API credentials")
                        st.markdown("**To enable auto-posting:**")
                        st.markdown("1. LinkedIn does not provide free posting API for personal accounts")
                        st.markdown("2. **Recommended:** Copy posts below and paste manually on LinkedIn")

                        with st.expander("📋 Selected Posts for Manual Publishing"):
                            for post_num, content in selected_for_publish:
                                st.markdown(f"**Post {post_num}:**")
                                st.code(content)
                                st.markdown("---")
            else:
                st.info("No LinkedIn posts generated")
        else:
            st.info("No platform posts")


def export_content(content):
    """Export content in various formats."""
    st.markdown("### 📥 Export Options")

    export_format = st.radio("Format", ["Text", "Markdown", "JSON"], horizontal=True)

    if export_format == "Text":
        text = format_as_text(content)
        st.download_button(
            "⬇️ Download TXT",
            text,
            file_name=f"content_{content.generation_id[:8]}.txt",
            mime="text/plain"
        )

    elif export_format == "Markdown":
        markdown = format_as_markdown(content)
        st.download_button(
            "⬇️ Download MD",
            markdown,
            file_name=f"content_{content.generation_id[:8]}.md",
            mime="text/markdown"
        )

    elif export_format == "JSON":
        import json
        json_str = json.dumps(content.model_dump(mode='json'), indent=2)
        st.download_button(
            "⬇️ Download JSON",
            json_str,
            file_name=f"content_{content.generation_id[:8]}.json",
            mime="application/json"
        )


def show_all_posts_for_copy(content):
    """Show all posts combined for easy copying."""
    st.markdown("### 📋 All Posts Combined")

    all_text = ""

    linkedin_posts = [p for p in content.platform_posts if p.platform == "linkedin"]

    if linkedin_posts:
        all_text += "=== LINKEDIN POSTS ===\n\n"
        for i, post in enumerate(linkedin_posts, 1):
            all_text += f"--- Post {i} ---\n{post.content}\n\n"

    st.code(all_text, language=None)


def format_as_text(content):
    """Format content as plain text."""
    lines = []
    lines.append(f"Generated: {content.generation_date}")
    lines.append(f"Profile: {content.profile_id}")
    lines.append(f"Status: {content.status.value}")
    lines.append("\n" + "="*60 + "\n")

    for i, topic in enumerate(content.topic_briefs, 1):
        lines.append(f"\nTOPIC {i}")
        lines.append(f"Core Insight: {topic.core_insight}")
        lines.append(f"Hook: {topic.potential_hook}\n")

    for post in content.platform_posts:
        lines.append(f"\n{post.platform.upper()} POST")
        lines.append(post.content)
        lines.append("")

    return "\n".join(lines)


def format_as_markdown(content):
    """Format content as markdown."""
    lines = []
    lines.append(f"# Content Generation Report")
    lines.append(f"\n**Generated:** {content.generation_date}")
    lines.append(f"**Profile:** {content.profile_id}")
    lines.append(f"**Status:** {content.status.value}\n")

    lines.append("## Topics\n")
    for i, topic in enumerate(content.topic_briefs, 1):
        lines.append(f"### Topic {i}")
        lines.append(f"**Core Insight:** {topic.core_insight}")
        lines.append(f"**Hook:** {topic.potential_hook}\n")

    lines.append("## Platform Posts\n")
    for post in content.platform_posts:
        lines.append(f"### {post.platform.title()} Post")
        lines.append(f"```\n{post.content}\n```\n")

    return "\n".join(lines)
