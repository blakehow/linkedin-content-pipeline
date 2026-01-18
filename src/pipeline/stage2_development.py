"""Stage 2: Content Development - Develop topic briefs into full content."""

import logging
import re
import uuid
from datetime import datetime
from typing import List, Dict

from src.data.models import TopicBrief, BrandProfile, DevelopedContent, ContentVersion
from src.ai.factory import get_ai_client
from src.ai.prompts import PromptManager

logger = logging.getLogger(__name__)


class ContentDeveloper:
    """Develops topic briefs into full content pieces."""

    def __init__(self):
        """Initialize the content developer."""
        self.ai_client = get_ai_client()
        self.prompt_manager = PromptManager()

    def develop_content(
        self,
        topic_brief: TopicBrief,
        profile: BrandProfile,
        versions: List[str] = None
    ) -> List[DevelopedContent]:
        """Develop a topic brief into content versions.

        Args:
            topic_brief: The topic to develop
            profile: Brand profile for context
            versions: List of version types (bridge, aspirational, current)
                     Default: all three

        Returns:
            List of DevelopedContent objects
        """
        if versions is None:
            versions = ["bridge", "aspirational", "current"]

        logger.info(f"Developing topic {topic_brief.topic_id} into {len(versions)} versions")

        # Prepare profile info
        profile_info = {
            "bio": profile.bio,
            "target_audience": profile.target_audience,
            "tone": profile.tone,
        }

        # Format topic brief
        topic_text = self._format_topic_brief(topic_brief)

        # Generate each version
        developed = []
        for version_type in versions:
            try:
                logger.info(f"Generating {version_type} version")
                content = self._generate_version(
                    topic_text,
                    version_type,
                    profile_info
                )
                developed.append(content)
            except Exception as e:
                logger.error(f"Failed to generate {version_type} version: {e}")

        logger.info(f"Successfully developed {len(developed)} content versions")
        return developed

    def _format_topic_brief(self, topic: TopicBrief) -> str:
        """Format topic brief for prompt."""
        return f"""
**Core Insight:** {topic.core_insight}

**Audience Resonance:** {topic.audience_resonance}

**Authentic Angle:** {topic.authentic_angle}

**Potential Hook:** {topic.potential_hook}
""".strip()

    def _generate_version(
        self,
        topic_text: str,
        version_type: str,
        profile_info: Dict
    ) -> DevelopedContent:
        """Generate a single content version."""

        # Map version type to enum
        version_map = {
            "bridge": ContentVersion.BRIDGE,
            "aspirational": ContentVersion.ASPIRATIONAL,
            "current": ContentVersion.CURRENT,
        }
        version_enum = version_map.get(version_type.lower(), ContentVersion.BRIDGE)

        # Render prompt
        prompt = self.prompt_manager.render_stage2(
            topic_text,
            version_type,
            profile_info
        )

        # Generate content
        response = self.ai_client.generate(prompt, max_tokens=3000)

        # Parse response
        parsed = self._parse_content(response)

        # Create DevelopedContent object
        content = DevelopedContent(
            content_id=f"content-{uuid.uuid4().hex[:8]}",
            topic_id=f"topic-{uuid.uuid4().hex[:8]}",  # Will be updated by orchestrator
            version=version_enum,
            title=parsed["title"],
            body=parsed["body"],
            key_statistics=parsed["statistics"],
            sources=parsed["sources"],
            examples=parsed["examples"],
            word_count=len(parsed["body"].split()),
            estimated_read_time=max(1, len(parsed["body"].split()) // 200),
            created_at=datetime.now()
        )

        return content

    def _parse_content(self, ai_response: str) -> Dict:
        """Parse AI response into structured content."""
        result = {
            "title": "Untitled",
            "body": "",
            "statistics": [],
            "sources": [],
            "examples": [],
        }

        lines = ai_response.strip().split("\n")

        # Extract title
        for line in lines[:5]:  # Check first 5 lines
            if line.startswith("**Title:**"):
                result["title"] = line.replace("**Title:**", "").strip()
                break
            elif line.startswith("#"):
                result["title"] = line.replace("#", "").strip()
                break

        # Extract main body (everything before "Key Statistics" or similar)
        body_lines = []
        in_body = True
        capture_stats = False
        capture_examples = False

        for line in lines:
            line = line.strip()

            # Check for section markers
            if "**Key Statistics:**" in line or "Key Statistics:" in line:
                in_body = False
                capture_stats = True
                capture_examples = False
                continue
            elif "**Examples:**" in line or "Examples:" in line:
                in_body = False
                capture_stats = False
                capture_examples = True
                continue
            elif "**Word Count:**" in line:
                break

            # Collect content based on section
            if in_body and line and not line.startswith("**Title:**"):
                body_lines.append(line)
            elif capture_stats and line.startswith("-") or line.startswith("•"):
                stat = line.lstrip("-•").strip()
                if stat:
                    result["statistics"].append(stat)
                    # Extract source URLs if present
                    urls = re.findall(r'https?://[^\s]+', stat)
                    result["sources"].extend(urls)
            elif capture_examples and line.startswith("-") or line.startswith("•"):
                example = line.lstrip("-•").strip()
                if example:
                    result["examples"].append(example)

        result["body"] = "\n".join(body_lines).strip()

        # If body is empty, use entire response
        if not result["body"]:
            result["body"] = ai_response.strip()

        return result
