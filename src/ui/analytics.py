"""Analytics UI page."""

import streamlit as st
from src.data.storage import get_storage
from collections import Counter


def show():
    """Display the analytics page."""

    st.title("📊 Analytics")
    st.markdown("Track your content performance and insights.")

    storage = get_storage()

    # Overall stats
    st.subheader("📈 Overview")

    col1, col2, col3, col4 = st.columns(4)

    ideas = storage.get_ideas()
    unused_ideas = storage.get_ideas(unused_only=True)
    content_list = storage.get_content_list()
    profiles = storage.get_profiles()

    with col1:
        st.metric("Total Ideas", len(ideas))
        st.caption(f"{len(unused_ideas)} unused")

    with col2:
        st.metric("Content Generated", len(content_list))

    with col3:
        total_posts = sum(len(c.platform_posts) for c in content_list)
        st.metric("Total Posts", total_posts)

    with col4:
        st.metric("Brand Profiles", len(profiles))

    st.markdown("---")

    # Ideas by category
    st.subheader("💡 Ideas by Category")

    if ideas:
        categories = Counter(idea.category for idea in ideas)

        col1, col2 = st.columns([2, 1])

        with col1:
            st.bar_chart(categories)

        with col2:
            for category, count in categories.most_common():
                st.metric(category, count)
    else:
        st.info("No ideas yet")

    st.markdown("---")

    # Content performance placeholder
    st.subheader("📊 Content Performance")

    st.info("""
    **Coming Soon:**
    - Post engagement metrics
    - Best performing topics
    - Optimal posting times
    - Content type analysis
    - Platform comparison

    Connect your LinkedIn and Twitter accounts to track performance automatically.
    """)

    # Recent activity
    st.markdown("---")
    st.subheader("📅 Recent Activity")

    if content_list:
        for content in content_list[:10]:
            with st.expander(
                f"{content.generation_date.strftime('%Y-%m-%d %H:%M')} - {len(content.platform_posts)} posts ({content.status.value})"
            ):
                st.write(f"**Profile:** {content.profile_id}")
                st.write(f"**Topics:** {len(content.topic_briefs)}")
                st.write(f"**Content Pieces:** {len(content.developed_content)}")
                st.write(f"**Platform Posts:** {len(content.platform_posts)}")

                platforms = set(post.platform for post in content.platform_posts)
                st.write(f"**Platforms:** {', '.join(platforms)}")
    else:
        st.info("No activity yet")
