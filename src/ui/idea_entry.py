"""Idea entry UI page."""

import streamlit as st
import uuid
from datetime import datetime

from src.data.models import Idea
from src.data.storage import get_storage
from src.security import sanitize_user_input
from src.ai.factory import create_ai_client


def show():
    """Display the idea entry page."""

    st.title("Add Content Ideas")
    st.markdown("Capture ideas, observations, and experiences that could become content.")

    storage = get_storage()
    settings = storage.get_settings()

    # Load categories from settings
    categories = settings.idea_categories if settings and hasattr(settings, 'idea_categories') else [
        "General", "Leadership", "Team Management", "Product Development",
        "Personal Growth", "AI & Technology", "Marketing", "Operations",
        "Customer Success", "Other"
    ]

    # Entry mode selection
    st.subheader("Add Content Ideas")

    # Check if we're editing an existing idea
    editing_idea = None
    if "editing_idea_id" in st.session_state:
        editing_idea_id = st.session_state["editing_idea_id"]
        editing_idea = storage.get_idea(editing_idea_id)

        if editing_idea:
            st.info(f"Editing: {editing_idea.title if editing_idea.title else 'Untitled'}")
            if st.button("Cancel Edit", use_container_width=True):
                del st.session_state["editing_idea_id"]
                st.rerun()
            st.markdown("---")

    entry_mode = st.radio(
        "Entry Mode",
        ["Quick Idea", "Journal Entry"],
        horizontal=True,
        help="Quick Idea: Short observations. Journal Entry: Longer reflections and stories."
    )

    with st.form("idea_form", clear_on_submit=False):
        # Pre-populate form if editing
        default_title = editing_idea.title if editing_idea and editing_idea.title else ""
        default_text = editing_idea.text if editing_idea else ""
        default_category = editing_idea.category if editing_idea else categories[0]

        # Title field
        title = st.text_input(
            "Title (Optional)",
            value=default_title,
            placeholder="Quick identifier for this idea",
            help="A short title to help you identify this idea later"
        )

        if entry_mode == "Quick Idea":
            idea_text = st.text_area(
                "Your Idea",
                value=default_text,
                placeholder="What did you notice? What did you learn? What insight do you have?",
                height=150,
                help="Write a quick observation, lesson learned, or pattern you noticed."
            )
        else:
            idea_text = st.text_area(
                "Journal Entry",
                value=default_text,
                placeholder="Tell a story... What happened? What did you learn? How did it make you feel? What would you do differently?",
                height=400,
                help="Write a longer journal entry. Include stories, context, emotions, and lessons. The AI will extract ideas from your writing."
            )

        # Category selection (using dynamic categories)
        try:
            cat_index = categories.index(default_category)
        except ValueError:
            cat_index = 0

        category = st.selectbox("Category", categories, index=cat_index)

        # Form buttons
        col1, col2 = st.columns(2)

        with col1:
            submitted = st.form_submit_button("Save Idea", type="primary", use_container_width=True)

        with col2:
            refine = st.form_submit_button("Refine with AI", use_container_width=True)

        if submitted:
            if not idea_text or len(idea_text.strip()) < 10:
                st.error("Please enter at least 10 characters for your idea.")
            else:
                try:
                    # Sanitize inputs
                    sanitized_text = sanitize_user_input(idea_text, input_type="idea")
                    sanitized_title = sanitize_user_input(title, input_type="general") if title else None

                    if editing_idea:
                        # Update existing idea (normal edit - don't touch refined_text)
                        editing_idea.title = sanitized_title
                        editing_idea.text = sanitized_text
                        editing_idea.category = category

                        # Mark as unused again since it's been edited
                        editing_idea.used = False
                        editing_idea.used_date = None

                        # Keep refined_text as is - don't overwrite during normal edit
                        storage.update_idea(editing_idea)

                        # Clear edit mode
                        del st.session_state["editing_idea_id"]
                        st.success("Idea updated and marked as new")
                        st.rerun()
                    else:
                        # Create new idea
                        idea = Idea(
                            id=f"idea-{uuid.uuid4().hex[:8]}",
                            timestamp=datetime.now(),
                            title=sanitized_title,
                            text=sanitized_text,
                            category=category,
                            used=False
                        )

                        storage.create_idea(idea)
                        st.success("Idea added successfully")
                        st.rerun()  # Rerun to clear the form
                except ValueError as e:
                    st.error(f"Invalid input: {str(e)}")

        if refine:
            if not idea_text or len(idea_text.strip()) < 10:
                st.error("Please enter at least 10 characters for your idea.")
            else:
                # Store data in session state for refinement
                st.session_state["refining"] = True
                st.session_state["original_text"] = idea_text
                st.session_state["original_title"] = title
                st.session_state["original_category"] = category
                st.rerun()

    # LLM Refinement Display
    if st.session_state.get("refining", False):
        st.markdown("---")

        with st.container(border=True):
            st.markdown("### AI Refinement")
            st.markdown("Review the AI-enhanced version of your idea and choose which version to save.")

            try:
                ai_client = create_ai_client()

                # Get the text from session state
                original_text = st.session_state.get('original_text', '')

                if not original_text:
                    st.error("No text captured. Please try entering your idea again.")
                    if st.button("Go Back"):
                        del st.session_state["refining"]
                        st.rerun()
                    return

                with st.spinner("Refining your idea with AI..."):
                    prompt = f"""Refine and enhance this content idea for LinkedIn.

Original idea: {original_text}

Please:
1. Clarify the core message
2. Add structure if needed
3. Make it more engaging and professional
4. Keep the authentic voice
5. Expand on key points briefly

Output only the refined version, no explanations."""

                    refined = ai_client.generate(prompt)

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Original:**")
                    st.text_area(
                        "Original version",
                        st.session_state["original_text"],
                        height=250,
                        disabled=True,
                        key="orig",
                        label_visibility="collapsed"
                    )

                with col2:
                    st.markdown("**Refined:**")
                    refined_text = st.text_area(
                        "Refined version (editable)",
                        refined,
                        height=250,
                        key="refined_edit",
                        label_visibility="collapsed"
                    )

                # Action buttons
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("Save Refined", type="primary", use_container_width=True):
                        try:
                            sanitized_refined = sanitize_user_input(refined_text, input_type="idea")
                            sanitized_title = sanitize_user_input(
                                st.session_state.get("original_title") or "",
                                input_type="general"
                            ) if st.session_state.get("original_title") else None

                            new_idea = Idea(
                                id=f"idea-{uuid.uuid4().hex[:8]}",
                                timestamp=datetime.now(),
                                title=sanitized_title,
                                text=st.session_state["original_text"],
                                refined_text=sanitized_refined,
                                category=st.session_state["original_category"]
                            )

                            storage.create_idea(new_idea)
                            del st.session_state["refining"]
                            del st.session_state["original_text"]
                            del st.session_state["original_title"]
                            del st.session_state["original_category"]
                            st.success("Refined idea saved")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"Invalid input: {str(e)}")

                with col2:
                    if st.button("Save Original", use_container_width=True):
                        try:
                            sanitized_text = sanitize_user_input(st.session_state["original_text"], input_type="idea")
                            sanitized_title = sanitize_user_input(
                                st.session_state.get("original_title") or "",
                                input_type="general"
                            ) if st.session_state.get("original_title") else None

                            new_idea = Idea(
                                id=f"idea-{uuid.uuid4().hex[:8]}",
                                timestamp=datetime.now(),
                                title=sanitized_title,
                                text=sanitized_text,
                                category=st.session_state["original_category"]
                            )

                            storage.create_idea(new_idea)
                            del st.session_state["refining"]
                            del st.session_state["original_text"]
                            del st.session_state["original_title"]
                            del st.session_state["original_category"]
                            st.success("Original idea saved")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"Invalid input: {str(e)}")

                with col3:
                    if st.button("Cancel", use_container_width=True):
                        del st.session_state["refining"]
                        del st.session_state["original_text"]
                        del st.session_state["original_title"]
                        del st.session_state["original_category"]
                        st.rerun()

            except Exception as e:
                error_msg = str(e)
                st.error(f"AI refinement failed: {error_msg}")

                # Provide helpful context based on error type
                error_lower = error_msg.lower()

                # Check if Gemini quota exceeded and Ollama was tried
                if "gemini" in error_lower and "quota" in error_lower:
                    if "ollama" in error_lower:
                        # Both services were tried
                        st.warning("**Gemini API quota exceeded.** The system tried to use Ollama as a fallback but it's not running. Please wait 24 hours for your Gemini quota to reset, or start the Ollama service locally.")
                        st.info("**To use Ollama:** Make sure the Ollama service is running (`ollama serve`)")
                    else:
                        # Only Gemini tried (no fallback configured)
                        st.warning("**Gemini API quota exceeded.** Please wait up to 24 hours for your quota to reset, or configure Ollama as a fallback service.")
                elif "rate limit" in error_lower:
                    st.warning("Rate limit reached. The system tried 3 times with exponential backoff. Please wait a few minutes and try again.")
                elif "timeout" in error_lower or "timed out" in error_lower:
                    st.warning("Request timed out. The AI service took too long to respond. Please try again.")
                elif "connection" in error_lower or "network" in error_lower:
                    st.warning("Network error. Please check your internet connection and try again.")
                elif "not available" in error_lower:
                    st.warning("AI service is not available. If using Ollama, make sure it's running (`ollama serve`).")
                else:
                    st.info("The system automatically retried the request but couldn't complete it. You can save the original idea and try refining later.")

                # Option to save original
                if st.button("Save Original Without Refinement", type="primary"):
                    try:
                        sanitized_text = sanitize_user_input(st.session_state["original_text"], input_type="idea")
                        sanitized_title = sanitize_user_input(
                            st.session_state.get("original_title") or "",
                            input_type="general"
                        ) if st.session_state.get("original_title") else None

                        new_idea = Idea(
                            id=f"idea-{uuid.uuid4().hex[:8]}",
                            timestamp=datetime.now(),
                            title=sanitized_title,
                            text=sanitized_text,
                            category=st.session_state["original_category"]
                        )

                        storage.create_idea(new_idea)
                        del st.session_state["refining"]
                        del st.session_state["original_text"]
                        del st.session_state["original_title"]
                        del st.session_state["original_category"]
                        st.success("Original idea saved")
                        st.rerun()
                    except ValueError as e:
                        st.error(f"Invalid input: {str(e)}")

    st.markdown("---")

    # View existing ideas
    st.subheader("Your Ideas")

    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        show_used = st.checkbox("Show used ideas", value=False)

    with col2:
        category_filter = st.selectbox(
            "Filter by category",
            ["All"] + categories
        )

    with col3:
        sort_order = st.selectbox(
            "Sort by",
            ["Newest first", "Oldest first"]
        )

    # Get ideas
    ideas = storage.get_ideas(unused_only=not show_used)

    # Apply filters
    if category_filter != "All":
        ideas = [idea for idea in ideas if idea.category == category_filter]

    # Sort
    if sort_order == "Oldest first":
        ideas = list(reversed(ideas))

    # Display ideas
    if not ideas:
        st.info("No ideas yet. Add your first idea above!")
    else:
        st.caption(f"Showing {len(ideas)} idea(s)")

        for idea in ideas:
            # Display title with date
            if hasattr(idea, 'title') and idea.title:
                display_header = f"{idea.title} • {idea.timestamp.strftime('%Y-%m-%d')}"
            else:
                display_header = f"{idea.category} • {idea.timestamp.strftime('%Y-%m-%d')}"

            with st.expander(
                f"{'[Used] ' if idea.used else ''}{display_header}",
                expanded=False
            ):
                # Show date and category in header
                col1, col2 = st.columns([3, 1])
                with col1:
                    if hasattr(idea, 'title') and idea.title:
                        st.markdown(f"### {idea.title}")
                with col2:
                    st.caption(f"📅 {idea.timestamp.strftime('%b %d, %Y')}")

                st.markdown(f"**Category:** {idea.category}")
                st.markdown("---")

                st.markdown("**Original:**")
                st.write(idea.text)

                # Show refined text if available
                if hasattr(idea, 'refined_text') and idea.refined_text:
                    st.markdown("---")
                    st.markdown("**Refined Version:**")
                    st.write(idea.refined_text)

                # Show status
                st.markdown("---")
                if idea.used:
                    st.caption(f"Used on {idea.used_date.strftime('%b %d, %Y') if idea.used_date else 'N/A'}")
                else:
                    st.caption("Unused")

                # Action buttons
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Edit", key=f"edit-{idea.id}", use_container_width=True):
                        # Load idea into main form at top
                        st.session_state["editing_idea_id"] = idea.id
                        st.rerun()

                with col2:
                    if st.button("Delete", key=f"delete-{idea.id}", use_container_width=True):
                        storage.delete_idea(idea.id)
                        st.success("Idea deleted")
                        st.rerun()
