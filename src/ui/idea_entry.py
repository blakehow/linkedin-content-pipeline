"""Idea entry UI page."""

import streamlit as st
import uuid
from datetime import datetime

from src.data.models import Idea
from src.data.storage import get_storage


def show():
    """Display the idea entry page."""

    st.title("💡 Add Content Ideas")
    st.markdown("Capture ideas, observations, and experiences that could become content.")

    storage = get_storage()

    # Idea entry form
    st.subheader("New Idea")

    with st.form("idea_form", clear_on_submit=True):
        idea_text = st.text_area(
            "Your Idea",
            placeholder="What did you notice? What did you learn? What insight do you have?",
            height=150,
            help="Write whatever comes to mind - a personal observation, a lesson learned, a pattern you noticed, etc."
        )

        col1, col2 = st.columns(2)

        with col1:
            category = st.selectbox(
                "Category",
                [
                    "General",
                    "Leadership",
                    "Team Management",
                    "Product Development",
                    "Personal Growth",
                    "AI & Technology",
                    "Marketing",
                    "Operations",
                    "Customer Success",
                    "Other"
                ]
            )

        with col2:
            source = st.text_input(
                "Source (Optional)",
                value="Web UI",
                help="Where did this idea come from?"
            )

        submitted = st.form_submit_button("Add Idea", type="primary", use_container_width=True)

        if submitted:
            if not idea_text or len(idea_text.strip()) < 10:
                st.error("Please enter at least 10 characters for your idea.")
            else:
                # Create idea
                idea = Idea(
                    id=f"idea-{uuid.uuid4().hex[:8]}",
                    timestamp=datetime.now(),
                    text=idea_text.strip(),
                    category=category,
                    source=source,
                    used=False
                )

                storage.create_idea(idea)
                st.success("✅ Idea added successfully!")
                st.balloons()

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
            ["All"] + [
                "General", "Leadership", "Team Management", "Product Development",
                "Personal Growth", "AI & Technology", "Marketing", "Operations",
                "Customer Success", "Other"
            ]
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
            with st.expander(
                f"{'✅ ' if idea.used else '💡 '}{idea.category} - {idea.timestamp.strftime('%Y-%m-%d %H:%M')}",
                expanded=False
            ):
                st.write(idea.text)

                col1, col2, col3 = st.columns([2, 2, 1])

                with col1:
                    st.caption(f"**Category:** {idea.category}")
                with col2:
                    st.caption(f"**Source:** {idea.source}")
                with col3:
                    if idea.used:
                        st.caption(f"✅ Used on {idea.used_date.strftime('%Y-%m-%d') if idea.used_date else 'N/A'}")
                    else:
                        st.caption("💡 Unused")

                # Action buttons
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Edit", key=f"edit-{idea.id}"):
                        st.session_state[f"editing_{idea.id}"] = True
                        st.rerun()

                with col2:
                    if st.button("Delete", key=f"delete-{idea.id}"):
                        storage.delete_idea(idea.id)
                        st.success("Idea deleted")
                        st.rerun()

                # Edit mode
                if st.session_state.get(f"editing_{idea.id}", False):
                    st.markdown("---")
                    with st.form(f"edit_form_{idea.id}"):
                        new_text = st.text_area("Edit idea", value=idea.text)
                        new_category = st.selectbox(
                            "Category",
                            [
                                "General", "Leadership", "Team Management", "Product Development",
                                "Personal Growth", "AI & Technology", "Marketing", "Operations",
                                "Customer Success", "Other"
                            ],
                            index=[
                                "General", "Leadership", "Team Management", "Product Development",
                                "Personal Growth", "AI & Technology", "Marketing", "Operations",
                                "Customer Success", "Other"
                            ].index(idea.category)
                        )

                        col1, col2 = st.columns(2)

                        with col1:
                            if st.form_submit_button("Save"):
                                idea.text = new_text
                                idea.category = new_category
                                storage.update_idea(idea)
                                del st.session_state[f"editing_{idea.id}"]
                                st.success("Idea updated!")
                                st.rerun()

                        with col2:
                            if st.form_submit_button("Cancel"):
                                del st.session_state[f"editing_{idea.id}"]
                                st.rerun()
