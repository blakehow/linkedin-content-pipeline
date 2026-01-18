"""Stage 3: Platform Optimization - Optimize content for LinkedIn and Twitter."""

import logging
import re
import uuid
from datetime import datetime
from typing import List, Dict

from src.data.models import DevelopedContent, BrandProfile, PlatformPost, UserSettings
from src.ai.factory import get_ai_client
from src.ai.prompts import PromptManager

logger = logging.getLogger(__name__)


class PlatformOptimizer:
    """Optimizes content for specific social media platforms."""

    def __init__(self):
        """Initialize the platform optimizer."""
        self.ai_client = get_ai_client()
        self.prompt_manager = PromptManager()

    def optimize_for_platforms(
        self,
        content: DevelopedContent,
        profile: BrandProfile,
        settings: UserSettings,
        platforms: List[str] = None
    ) -> List[PlatformPost]:
        """Optimize content for target platforms.

        Args:
            content: Developed content to optimize
            profile: Brand profile
            settings: User settings (emoji usage, hashtags, etc.)
            platforms: List of platforms (linkedin, twitter). Default: both

        Returns:
            List of PlatformPost objects
        """
        if platforms is None:
            platforms = ["linkedin", "twitter"]

        logger.info(f"Optimizing content {content.content_id} for {platforms}")

        posts = []

        # Prepare profile info
        profile_info = {"bio": profile.bio}

        if "linkedin" in platforms:
            linkedin_posts = self._optimize_linkedin(
                content,
                profile_info,
                settings
            )
            posts.extend(linkedin_posts)

        if "twitter" in platforms:
            twitter_posts = self._optimize_twitter(
                content,
                profile_info,
                settings
            )
            posts.extend(twitter_posts)

        logger.info(f"Generated {len(posts)} optimized posts")
        return posts

    def _optimize_linkedin(
        self,
        content: DevelopedContent,
        profile_info: Dict,
        settings: UserSettings
    ) -> List[PlatformPost]:
        """Generate LinkedIn-optimized variations."""

        # Render prompt
        prompt = self.prompt_manager.render_stage3_linkedin(
            developed_content=f"**{content.title}**\n\n{content.body}",
            profile_info=profile_info,
            emoji_usage=settings.emoji_usage.value,
            max_hashtags=settings.max_hashtags
        )

        # Generate
        response = self.ai_client.generate(prompt, max_tokens=2500)

        # Parse variations
        variations = self._parse_linkedin_variations(response)

        # Create PlatformPost objects
        posts = []
        for i, var in enumerate(variations, 1):
            post = PlatformPost(
                post_id=f"linkedin-{uuid.uuid4().hex[:8]}",
                content_id=content.content_id,
                platform="LinkedIn",
                text=var["text"],
                hashtags=var["hashtags"],
                character_count=len(var["text"]),
                variation_number=i,
                hook_style=var["hook_style"],
                created_at=datetime.now()
            )
            posts.append(post)

        return posts

    def _optimize_twitter(
        self,
        content: DevelopedContent,
        profile_info: Dict,
        settings: UserSettings
    ) -> List[PlatformPost]:
        """Generate Twitter thread variations."""

        # Render prompt
        prompt = self.prompt_manager.render_stage3_twitter(
            developed_content=f"**{content.title}**\n\n{content.body}",
            profile_info=profile_info,
            emoji_usage=settings.emoji_usage.value,
            max_hashtags=min(settings.max_hashtags, 3)  # Twitter: fewer hashtags
        )

        # Generate
        response = self.ai_client.generate(prompt, max_tokens=2500)

        # Parse threads
        threads = self._parse_twitter_threads(response)

        # Create PlatformPost objects
        posts = []
        for i, thread in enumerate(threads, 1):
            # Join thread into single text with newlines
            full_text = "\n\n".join(thread["tweets"])

            post = PlatformPost(
                post_id=f"twitter-{uuid.uuid4().hex[:8]}",
                content_id=content.content_id,
                platform="Twitter",
                text=full_text,
                hashtags=thread["hashtags"],
                character_count=len(full_text),
                variation_number=i,
                hook_style=thread.get("thread_type", "Standard"),
                is_thread=True,
                thread_parts=thread["tweets"],
                created_at=datetime.now()
            )
            posts.append(post)

        return posts

    def _parse_linkedin_variations(self, ai_response: str) -> List[Dict]:
        """Parse LinkedIn variations from AI response."""
        variations = []

        # Split by variation markers
        sections = re.split(r'## Variation \d+:', ai_response)

        for section in sections[1:]:  # Skip first empty split
            try:
                lines = section.strip().split("\n")

                # Extract variation details
                text_lines = []
                hashtags = []
                hook_style = "Standard"

                capture_text = True

                for line in lines:
                    line = line.strip()

                    if line.startswith("**Character Count:**"):
                        capture_text = False
                    elif line.startswith("**Hook Style:**"):
                        hook_style = line.replace("**Hook Style:**", "").strip()
                    elif line.startswith("**Hashtags:**"):
                        # Extract hashtags
                        hashtag_text = line.replace("**Hashtags:**", "").strip()
                        hashtags = [tag.strip() for tag in hashtag_text.split() if tag.startswith("#")]
                    elif capture_text and line and not line.startswith("**") and not line.startswith("---"):
                        text_lines.append(line)

                text = "\n".join(text_lines).strip()

                if text:
                    variations.append({
                        "text": text,
                        "hashtags": hashtags,
                        "hook_style": hook_style
                    })

            except Exception as e:
                logger.warning(f"Failed to parse LinkedIn variation: {e}")

        # If no variations parsed, create one from entire response
        if not variations:
            variations.append({
                "text": ai_response.strip(),
                "hashtags": [],
                "hook_style": "Standard"
            })

        return variations

    def _parse_twitter_threads(self, ai_response: str) -> List[Dict]:
        """Parse Twitter threads from AI response."""
        threads = []

        # Split by thread markers
        sections = re.split(r'## Thread [A-Z]:', ai_response)

        for section in sections[1:]:  # Skip first empty split
            try:
                lines = section.strip().split("\n")

                tweets = []
                hashtags = []
                thread_type = "Standard"

                for line in lines:
                    line = line.strip()

                    # Check for tweet (numbered like "1/", "2/", etc.)
                    if re.match(r'^\d+/', line):
                        # Extract tweet text
                        tweet_text = line.split("/", 1)[1].strip() if "/" in line else line
                        tweets.append(tweet_text)

                    elif line.startswith("**Thread Length:**"):
                        continue
                    elif line.startswith("**Hashtags:**"):
                        hashtag_text = line.replace("**Hashtags:**", "").strip()
                        hashtags = [tag.strip() for tag in hashtag_text.split() if tag.startswith("#")]
                    elif "Standard Format" in line or "Rapid-Fire" in line:
                        thread_type = "Standard" if "Standard" in line else "Rapid-Fire"

                if tweets:
                    threads.append({
                        "tweets": tweets,
                        "hashtags": hashtags,
                        "thread_type": thread_type
                    })

            except Exception as e:
                logger.warning(f"Failed to parse Twitter thread: {e}")

        # If no threads parsed, create one generic thread
        if not threads:
            threads.append({
                "tweets": [ai_response.strip()],
                "hashtags": [],
                "thread_type": "Standard"
            })

        return threads
