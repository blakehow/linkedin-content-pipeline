"""Settings UI page."""

import streamlit as st
import uuid
from datetime import datetime

from src.data.models import (
    UserSettings, BrandProfile, ProfileType, PlatformPriority, EmojiUsage
)
from src.data.storage import get_storage


def show():
    """Display the settings page."""

    st.title("⚙️ Settings")

    storage = get_storage()

    tabs = st.tabs(["👤 User Profile", "🏢 Brand Profiles", "🎨 Content Preferences"])

    # === TAB 1: User Profile ===
    with tabs[0]:
        st.subheader("User Profile")

        settings = storage.get_settings()

        with st.form("user_settings"):
            full_name = st.text_input(
                "Full Name",
                value=settings.user_full_name if settings else ""
            )

            col1, col2 = st.columns(2)

            with col1:
                linkedin_username = st.text_input(
                    "LinkedIn Username",
                    value=settings.linkedin_username if settings else "",
                    help="Your LinkedIn profile username or URL"
                )

            with col2:
                twitter_username = st.text_input(
                    "Twitter/X Username",
                    value=settings.twitter_username if settings else "",
                    help="Your Twitter handle (with or without @)"
                )

            notification_email = st.text_input(
                "Notification Email (Optional)",
                value=settings.notification_email if settings else ""
            )

            if st.form_submit_button("Save User Profile", type="primary"):
                if not full_name:
                    st.error("Full name is required")
                else:
                    if settings:
                        settings.user_full_name = full_name
                        settings.linkedin_username = linkedin_username
                        settings.twitter_username = twitter_username
                        if notification_email:
                            settings.notification_email = notification_email
                    else:
                        settings = UserSettings(
                            user_full_name=full_name,
                            linkedin_username=linkedin_username or None,
                            twitter_username=twitter_username or None,
                            notification_email=notification_email or None
                        )

                    storage.save_settings(settings)
                    st.success("✅ User profile saved!")
                    st.rerun()

    # === TAB 2: Brand Profiles ===
    with tabs[1]:
        st.subheader("Brand Profiles")

        st.markdown("""
        Create different profiles for different types of content you want to generate
        (e.g., Personal Brand, Company Brand, Product Marketing).
        """)

        # List existing profiles
        profiles = storage.get_profiles(active_only=False)

        if profiles:
            st.markdown("### Your Profiles")

            for profile in profiles:
                with st.expander(
                    f"{'✅ ' if profile.is_active else '❌ '}{profile.profile_name} ({profile.profile_type.value})"
                ):
                    st.write(f"**Target Audience:** {profile.target_audience}")
                    st.write(f"**Tone:** {profile.tone}")
                    st.write(f"**Key Topics:** {', '.join(profile.key_topics)}")
                    st.write(f"**Platform Priority:** {profile.platform_priority.value}")
                    st.write(f"**Bio:** {profile.bio}")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if not profile.is_active:
                            if st.button("Activate", key=f"activate-{profile.profile_id}"):
                                profile.is_active = True
                                storage.update_profile(profile)

                                # Set as active profile
                                settings = storage.get_settings()
                                if settings:
                                    settings.active_profile_id = profile.profile_id
                                    storage.save_settings(settings)

                                st.success("Profile activated!")
                                st.rerun()

                    with col2:
                        if profile.is_active:
                            if st.button("Deactivate", key=f"deactivate-{profile.profile_id}"):
                                profile.is_active = False
                                storage.update_profile(profile)
                                st.success("Profile deactivated!")
                                st.rerun()

                    with col3:
                        if st.button("Delete", key=f"delete-{profile.profile_id}"):
                            storage.delete_profile(profile.profile_id)
                            st.success("Profile deleted!")
                            st.rerun()

        # Create new profile
        st.markdown("---")
        st.markdown("### Create New Profile")

        with st.form("new_profile"):
            profile_name = st.text_input("Profile Name", placeholder="e.g., Personal Brand")

            profile_type = st.selectbox(
                "Profile Type",
                [pt.value for pt in ProfileType]
            )

            target_audience = st.text_input(
                "Target Audience",
                placeholder="e.g., Tech founders and leaders"
            )

            tone = st.text_input(
                "Tone & Voice",
                placeholder="e.g., Authentic, vulnerable, insightful"
            )

            key_topics = st.text_input(
                "Key Topics (comma-separated)",
                placeholder="e.g., Leadership, AI, Startups"
            )

            platform_priority = st.selectbox(
                "Platform Priority",
                [pp.value for pp in PlatformPriority]
            )

            bio = st.text_area(
                "Bio / Description",
                placeholder="Brief description of this brand/persona",
                height=100
            )

            if st.form_submit_button("Create Profile", type="primary"):
                if not all([profile_name, target_audience, tone, bio]):
                    st.error("Please fill in all required fields")
                else:
                    topics_list = [t.strip() for t in key_topics.split(",") if t.strip()]

                    new_profile = BrandProfile(
                        profile_id=f"profile-{uuid.uuid4().hex[:8]}",
                        profile_name=profile_name,
                        profile_type=ProfileType(profile_type),
                        target_audience=target_audience,
                        tone=tone,
                        key_topics=topics_list,
                        platform_priority=PlatformPriority(platform_priority),
                        bio=bio,
                        is_active=True,
                        created_at=datetime.now()
                    )

                    storage.create_profile(new_profile)

                    # Set as active if first profile
                    if len(profiles) == 0:
                        settings = storage.get_settings()
                        if settings:
                            settings.active_profile_id = new_profile.profile_id
                            storage.save_settings(settings)

                    st.success("✅ Profile created!")
                    st.rerun()

    # === TAB 3: Content Preferences ===
    with tabs[2]:
        st.subheader("Content Preferences")

        settings = storage.get_settings()

        if not settings:
            st.warning("Please set up your user profile first")
            return

        with st.form("content_prefs"):
            content_tone = st.text_input(
                "Default Content Tone",
                value=settings.content_tone_default
            )

            emoji_usage = st.select_slider(
                "Emoji Usage",
                options=[e.value for e in EmojiUsage],
                value=settings.emoji_usage.value
            )

            include_hashtags = st.checkbox(
                "Include Hashtags",
                value=settings.include_hashtags
            )

            max_hashtags = st.slider(
                "Maximum Hashtags",
                min_value=0,
                max_value=10,
                value=settings.max_hashtags
            )

            if st.form_submit_button("Save Preferences", type="primary"):
                settings.content_tone_default = content_tone
                settings.emoji_usage = EmojiUsage(emoji_usage)
                settings.include_hashtags = include_hashtags
                settings.max_hashtags = max_hashtags

                storage.save_settings(settings)
                st.success("✅ Preferences saved!")
                st.rerun()
