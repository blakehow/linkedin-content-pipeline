"""Stage 1: Topic Curation - Generate topic briefs from ideas."""

import logging
import uuid
from datetime import datetime
from typing import List

from src.data.models import Idea, BrandProfile, TopicBrief
from src.ai.factory import get_ai_client
from src.ai.prompts import PromptManager

logger = logging.getLogger(__name__)


class TopicCurator:
    """Curates topic briefs from user ideas."""

    def __init__(self):
        """Initialize the topic curator."""
        self.ai_client = get_ai_client()
        self.prompt_manager = PromptManager()

    def curate_topics(
        self,
        ideas: List[Idea],
        profile: BrandProfile,
        num_topics: int = 5
    ) -> List[TopicBrief]:
        """Curate topic briefs from ideas.

        Args:
            ideas: List of idea objects to analyze
            profile: Brand profile with audience/tone info
            num_topics: Number of topics to generate (default 5)

        Returns:
            List of TopicBrief objects
        """
        if not ideas:
            raise ValueError("No ideas provided for curation")

        logger.info(f"Curating {num_topics} topics from {len(ideas)} ideas")

        # Format ideas for prompt
        ideas_text = self._format_ideas(ideas)

        # Prepare profile info for prompt
        profile_info = {
            "bio": profile.bio,
            "target_audience": profile.target_audience,
            "tone": profile.tone,
            "key_topics": profile.key_topics,
            "platform_priority": profile.platform_priority.value,
        }

        # Render prompt
        prompt = self.prompt_manager.render_stage1(ideas_text, profile_info)

        # Generate topics
        logger.info("Calling AI to generate topics")
        response = self.ai_client.generate(prompt, max_tokens=2000)

        # Parse response into TopicBrief objects
        topics = self._parse_topics(response, ideas)

        logger.info(f"Successfully curated {len(topics)} topics")
        return topics

    def _format_ideas(self, ideas: List[Idea]) -> str:
        """Format ideas into text for the prompt."""
        formatted = []

        for i, idea in enumerate(ideas, 1):
            formatted.append(f"**Idea {i}** (Category: {idea.category})")
            formatted.append(idea.text)
            formatted.append("")  # Blank line

        return "\n".join(formatted)

    def _parse_topics(self, ai_response: str, source_ideas: List[Idea]) -> List[TopicBrief]:
        """Parse AI response into TopicBrief objects.

        This is a simple parser. In production, you might use more robust parsing
        or structured output from the AI.
        """
        topics = []
        source_idea_ids = [idea.id for idea in source_ideas]

        # Split by topic sections
        sections = ai_response.split("**Topic ")

        for section in sections[1:]:  # Skip first empty split
            try:
                # Extract topic number and content
                lines = section.strip().split("\n")

                # Find key components
                core_insight = ""
                audience_resonance = ""
                authentic_angle = ""
                potential_hook = ""
                title = lines[0].split(":", 1)[1].strip() if ":" in lines[0] else "Untitled"

                for line in lines:
                    line = line.strip()
                    if line.startswith("**Core Insight:**"):
                        core_insight = line.replace("**Core Insight:**", "").strip()
                    elif line.startswith("**Audience Resonance:**"):
                        audience_resonance = line.replace("**Audience Resonance:**", "").strip()
                    elif line.startswith("**Authentic Angle:**"):
                        authentic_angle = line.replace("**Authentic Angle:**", "").strip()
                    elif line.startswith("**Potential Hook:**"):
                        potential_hook = line.replace("**Potential Hook:**", "").strip()

                # Create TopicBrief
                if core_insight:  # Only add if we found core content
                    topic = TopicBrief(
                        topic_id=f"topic-{uuid.uuid4().hex[:8]}",
                        core_insight=core_insight,
                        audience_resonance=audience_resonance,
                        authentic_angle=authentic_angle,
                        potential_hook=potential_hook,
                        source_idea_ids=source_idea_ids,
                        created_at=datetime.now()
                    )
                    topics.append(topic)

            except Exception as e:
                logger.warning(f"Failed to parse topic section: {e}")
                continue

        # If parsing failed, create at least one generic topic
        if not topics and source_ideas:
            logger.warning("Failed to parse topics, creating generic topic")
            topics.append(TopicBrief(
                topic_id=f"topic-{uuid.uuid4().hex[:8]}",
                core_insight="Generated from your recent ideas",
                audience_resonance="Relevant to your target audience",
                authentic_angle="Based on your personal experiences",
                potential_hook="Here's what I learned...",
                source_idea_ids=source_idea_ids,
                created_at=datetime.now()
            ))

        return topics
