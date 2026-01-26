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

    st.title("Settings")

    storage = get_storage()

    tabs = st.tabs(["User Profile", "Brand Profiles", "Content Preferences", "Idea Categories", "AI Configuration"])

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
                # Twitter removed - LinkedIn only
                st.info("LinkedIn-only platform")

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
                        # Twitter removed
                        if notification_email:
                            settings.notification_email = notification_email
                    else:
                        settings = UserSettings(
                            user_full_name=full_name,
                            linkedin_username=linkedin_username or None,
                            twitter_username=None,
                            notification_email=notification_email or None
                        )

                    storage.save_settings(settings)
                    st.success("User profile saved")
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

                    st.markdown("---")

                    col1, col2, col3, col4 = st.columns(4)

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
                        if st.button("✏️ Edit", key=f"edit-{profile.profile_id}"):
                            st.session_state[f"editing_{profile.profile_id}"] = True
                            st.rerun()

                    with col4:
                        if st.button("🗑️ Delete", key=f"delete-{profile.profile_id}"):
                            storage.delete_profile(profile.profile_id)
                            st.success("Profile deleted!")
                            st.rerun()

                    # Edit mode
                    if st.session_state.get(f"editing_{profile.profile_id}", False):
                        st.markdown("---")
                        st.markdown("**✏️ Edit Profile:**")

                        with st.form(f"edit_form_{profile.profile_id}"):
                            edit_name = st.text_input("Profile Name", value=profile.profile_name)
                            edit_audience = st.text_input("Target Audience", value=profile.target_audience)
                            edit_tone = st.text_input("Tone & Voice", value=profile.tone)
                            edit_topics = st.text_input(
                                "Key Topics (comma-separated)",
                                value=", ".join(profile.key_topics) if profile.key_topics else ""
                            )
                            edit_bio = st.text_area(
                                "Bio / Description",
                                value=profile.bio,
                                height=100,
                                help="Paste your bio here. Maximum 500 characters."
                            )

                            # Character counter for edit
                            if edit_bio:
                                char_count = len(edit_bio)
                                if char_count > 500:
                                    st.error(f"❌ Bio too long: {char_count}/500 characters")
                                elif char_count < 10:
                                    st.warning(f"⚠️ Bio too short: {char_count}/500 characters")
                                else:
                                    st.caption(f"✅ {char_count}/500 characters")

                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("💾 Save Changes", type="primary"):
                                    if len(edit_bio) < 10 or len(edit_bio) > 500:
                                        st.error("Bio must be between 10 and 500 characters")
                                    else:
                                        profile.profile_name = edit_name
                                        profile.target_audience = edit_audience
                                        profile.tone = edit_tone
                                        profile.key_topics = [t.strip() for t in edit_topics.split(",") if t.strip()]
                                        profile.bio = edit_bio
                                        storage.update_profile(profile)
                                        del st.session_state[f"editing_{profile.profile_id}"]
                                        st.success("Profile updated")
                                        st.rerun()
                            with col2:
                                if st.form_submit_button("❌ Cancel"):
                                    del st.session_state[f"editing_{profile.profile_id}"]
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
                placeholder="Brief description of this brand/persona (10-500 characters)",
                height=100,
                help="Paste your bio here. Maximum 500 characters."
            )

            # Character counter
            if bio:
                char_count = len(bio)
                if char_count > 500:
                    st.error(f"❌ Bio too long: {char_count}/500 characters. Please shorten by {char_count - 500} characters.")
                elif char_count < 10:
                    st.warning(f"⚠️ Bio too short: {char_count}/500 characters. Need at least 10 characters.")
                else:
                    st.caption(f"✅ {char_count}/500 characters")

            if st.form_submit_button("Create Profile", type="primary"):
                if not all([profile_name, target_audience, tone, bio]):
                    st.error("Please fill in all required fields")
                elif len(bio) < 10:
                    st.error("Bio must be at least 10 characters")
                elif len(bio) > 500:
                    st.error("Bio must be 500 characters or less")
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

                    st.success("Profile created")
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
                st.success("Preferences saved")
                st.rerun()

    # === TAB 4: Idea Categories ===
    with tabs[3]:
        st.subheader("Idea Categories")
        st.markdown("Manage custom categories for organizing your content ideas.")

        settings = storage.get_settings()

        if not settings:
            st.warning("Please set up your user profile first")
            return

        st.markdown("### Current Categories")

        # Display current categories with delete buttons
        categories = settings.idea_categories

        for category in categories:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(f"• {category}")
            with col2:
                if st.button("🗑️", key=f"del-cat-{category}"):
                    settings.idea_categories.remove(category)
                    storage.save_settings(settings)
                    st.success(f"Deleted category: {category}")
                    st.rerun()

        st.markdown("---")

        # Add new category form
        st.markdown("### Add New Category")

        with st.form("new_category"):
            new_cat = st.text_input("Category Name", placeholder="e.g., Product Strategy")

            if st.form_submit_button("Add Category", type="primary"):
                if not new_cat:
                    st.error("Please enter a category name")
                elif new_cat in settings.idea_categories:
                    st.error(f"Category '{new_cat}' already exists")
                else:
                    settings.idea_categories.append(new_cat)
                    storage.save_settings(settings)
                    st.success(f"Added category: {new_cat}")
                    st.rerun()

    # === TAB 5: AI Configuration ===
    with tabs[4]:
        st.subheader("AI Provider Configuration")
        st.markdown("Configure which AI services to use for content generation.")

        settings = storage.get_settings()

        if not settings:
            st.warning("Please set up your user profile first")
            return

        # AI provider options
        ai_options = ["gemini", "ollama", "mock", "none"]

        with st.form("ai_config"):
            st.markdown("### Primary AI Provider")
            st.caption("The system will try this provider first for all AI operations.")

            primary = st.selectbox(
                "Primary Provider",
                options=ai_options,
                index=ai_options.index(settings.ai_provider_primary) if hasattr(settings, 'ai_provider_primary') and settings.ai_provider_primary in ai_options else 0,
                help="Gemini: Google's AI (requires API key, 1,500 free requests/day)\nOllama: Local AI (unlimited, no API key needed)\nMock: Test mode with sample data"
            )

            st.markdown("### Fallback AI Provider")
            st.caption("If the primary provider fails or hits quota limits, the system will automatically try this provider.")

            fallback = st.selectbox(
                "Fallback Provider",
                options=ai_options,
                index=ai_options.index(settings.ai_provider_fallback) if hasattr(settings, 'ai_provider_fallback') and settings.ai_provider_fallback in ai_options else 1,
                help="Choose a different provider than primary, or 'none' to disable fallback"
            )

            # Status indicators
            st.markdown("---")
            st.markdown("### Current Status")

            col1, col2 = st.columns(2)

            with col1:
                # Check Gemini status
                from config.settings import get_settings as get_env_settings
                env_settings = get_env_settings()

                if env_settings.google_gemini_api_key:
                    st.success("Gemini: API key configured")
                else:
                    st.warning("Gemini: No API key in .env")

            with col2:
                # Check Ollama status
                try:
                    import requests
                    response = requests.get("http://localhost:11434/api/version", timeout=2)
                    if response.status_code == 200:
                        st.success("Ollama: Running")
                    else:
                        st.error("Ollama: Not responding")
                except:
                    st.error("Ollama: Not running")

            st.markdown("---")

            if st.form_submit_button("Save AI Configuration", type="primary"):
                # Validation
                if primary == fallback and primary != "none":
                    st.error("Primary and fallback providers must be different")
                else:
                    settings.ai_provider_primary = primary
                    settings.ai_provider_fallback = fallback
                    storage.save_settings(settings)

                    # Reset global AI client to pick up new settings
                    import src.ai.factory as factory
                    factory._ai_client = None

                    st.success("AI configuration saved! The new settings will take effect immediately.")
                    st.rerun()
