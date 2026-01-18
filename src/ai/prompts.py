"""Prompt template management and rendering."""

from pathlib import Path
from typing import Dict, Any
from config.settings import PROMPTS_DIR


class PromptManager:
    """Manages prompt templates and variable substitution."""

    @staticmethod
    def load_template(template_name: str) -> str:
        """Load a prompt template from file."""
        template_path = PROMPTS_DIR / f"{template_name}.txt"

        if not template_path.exists():
            raise FileNotFoundError(f"Prompt template not found: {template_path}")

        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def render(template: str, variables: Dict[str, Any]) -> str:
        """Render a template with variables."""
        rendered = template

        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            rendered = rendered.replace(placeholder, str(value))

        return rendered

    @classmethod
    def render_stage1(cls, ideas_text: str, profile_info: Dict[str, Any]) -> str:
        """Render Stage 1 topic curation prompt."""
        template = cls.load_template("stage1_topic_curation")

        variables = {
            "ideas_text": ideas_text,
            "profile_info": profile_info.get("bio", ""),
            "target_audience": profile_info.get("target_audience", "professionals"),
            "key_topics": ", ".join(profile_info.get("key_topics", [])),
            "tone": profile_info.get("tone", "professional and friendly"),
            "platform_priority": profile_info.get("platform_priority", "both platforms equally"),
        }

        return cls.render(template, variables)

    @classmethod
    def render_stage2(
        cls,
        topic_brief: str,
        content_type: str,
        profile_info: Dict[str, Any]
    ) -> str:
        """Render Stage 2 content development prompt."""

        # Select template based on content type
        template_map = {
            "bridge": "stage2_content_bridge",
            "aspirational": "stage2_content_aspirational",
            "current": "stage2_content_current",
        }

        template_name = template_map.get(content_type.lower(), "stage2_content_bridge")
        template = cls.load_template(template_name)

        variables = {
            "topic_brief": topic_brief,
            "profile_info": profile_info.get("bio", ""),
            "target_audience": profile_info.get("target_audience", "professionals"),
            "tone": profile_info.get("tone", "professional and friendly"),
        }

        return cls.render(template, variables)

    @classmethod
    def render_stage3_linkedin(
        cls,
        developed_content: str,
        profile_info: Dict[str, Any],
        emoji_usage: str = "Moderate",
        max_hashtags: int = 5
    ) -> str:
        """Render Stage 3 LinkedIn optimization prompt."""
        template = cls.load_template("stage3_linkedin_optimize")

        variables = {
            "developed_content": developed_content,
            "profile_info": profile_info.get("bio", ""),
            "emoji_usage": emoji_usage,
            "max_hashtags": max_hashtags,
        }

        return cls.render(template, variables)

    @classmethod
    def render_stage3_twitter(
        cls,
        developed_content: str,
        profile_info: Dict[str, Any],
        emoji_usage: str = "Moderate",
        max_hashtags: int = 3
    ) -> str:
        """Render Stage 3 Twitter optimization prompt."""
        template = cls.load_template("stage3_twitter_optimize")

        variables = {
            "developed_content": developed_content,
            "profile_info": profile_info.get("bio", ""),
            "emoji_usage": emoji_usage,
            "max_hashtags": max_hashtags,
        }

        return cls.render(template, variables)
