"""Pipeline orchestrator - runs all three stages together."""

import logging
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from src.data.models import (
    GeneratedContent,
    ContentStatus,
    TopicBrief,
    DevelopedContent,
    PlatformPost
)
from src.data.storage import get_storage
from src.pipeline.stage1_curation import TopicCurator
from src.pipeline.stage2_development import ContentDeveloper
from src.pipeline.stage3_optimization import PlatformOptimizer

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Orchestrates the full content generation pipeline."""

    def __init__(self):
        """Initialize the orchestrator."""
        self.storage = get_storage()
        self.stage1 = TopicCurator()
        self.stage2 = ContentDeveloper()
        self.stage3 = PlatformOptimizer()

    def run_full_pipeline(
        self,
        profile_id: str,
        num_ideas: int = 10,
        num_topics: int = 5,
        content_versions: Optional[List[str]] = None,
        platforms: Optional[List[str]] = None,
        progress_callback: Optional[callable] = None
    ) -> GeneratedContent:
        """Run the complete 3-stage pipeline.

        Args:
            profile_id: Brand profile ID to use
            num_ideas: Number of unused ideas to pull
            num_topics: Number of topics to curate (default 5)
            content_versions: Which versions to generate (bridge, aspirational, current)
            platforms: Which platforms to optimize for (linkedin, twitter)
            progress_callback: Optional callback for progress updates

        Returns:
            GeneratedContent object with all outputs
        """
        logger.info("=== Starting Full Pipeline ===")
        self._update_progress(progress_callback, "Starting pipeline...", 0)

        # Get profile and settings
        profile = self.storage.get_profile(profile_id)
        if not profile:
            raise ValueError(f"Profile not found: {profile_id}")

        settings = self.storage.get_settings()
        if not settings:
            raise ValueError("User settings not configured")

        # Get unused ideas
        self._update_progress(progress_callback, "Loading ideas...", 5)
        ideas = self.storage.get_ideas(unused_only=True, limit=num_ideas)

        if not ideas:
            raise ValueError("No unused ideas available. Please add some ideas first.")

        logger.info(f"Using {len(ideas)} ideas")

        # Initialize result object
        generation_id = f"gen-{uuid.uuid4().hex[:8]}"
        result = GeneratedContent(
            generation_id=generation_id,
            generation_date=datetime.now(),
            profile_id=profile_id,
            source_idea_ids=[idea.id for idea in ideas],
            status=ContentStatus.DRAFT
        )

        # === STAGE 1: Topic Curation ===
        self._update_progress(progress_callback, "Stage 1: Curating topics...", 15)
        logger.info("--- Stage 1: Topic Curation ---")

        topic_briefs = self.stage1.curate_topics(
            ideas=ideas,
            profile=profile,
            num_topics=num_topics
        )

        result.topic_briefs = topic_briefs
        logger.info(f"Curated {len(topic_briefs)} topics")

        # === STAGE 2: Content Development ===
        self._update_progress(progress_callback, "Stage 2: Developing content...", 35)
        logger.info("--- Stage 2: Content Development ---")

        if content_versions is None:
            content_versions = ["bridge"]  # Default to bridge only for speed

        developed_content = []
        for i, topic in enumerate(topic_briefs):
            progress = 35 + (i / len(topic_briefs)) * 40  # 35-75%
            self._update_progress(
                progress_callback,
                f"Developing topic {i+1}/{len(topic_briefs)}...",
                progress
            )

            contents = self.stage2.develop_content(
                topic_brief=topic,
                profile=profile,
                versions=content_versions
            )

            # Update topic_id reference
            for content in contents:
                content.topic_id = topic.topic_id

            developed_content.extend(contents)

        result.developed_content = developed_content
        logger.info(f"Developed {len(developed_content)} content pieces")

        # === STAGE 3: Platform Optimization ===
        self._update_progress(progress_callback, "Stage 3: Optimizing for platforms...", 75)
        logger.info("--- Stage 3: Platform Optimization ---")

        if platforms is None:
            # Determine platforms from profile priority
            if profile.platform_priority.value == "LinkedIn primary":
                platforms = ["linkedin"]
            elif profile.platform_priority.value == "Twitter primary":
                platforms = ["twitter"]
            else:
                platforms = ["linkedin", "twitter"]

        platform_posts = []
        for i, content in enumerate(developed_content):
            progress = 75 + (i / len(developed_content)) * 20  # 75-95%
            self._update_progress(
                progress_callback,
                f"Optimizing content {i+1}/{len(developed_content)}...",
                progress
            )

            posts = self.stage3.optimize_for_platforms(
                content=content,
                profile=profile,
                settings=settings,
                platforms=platforms
            )

            platform_posts.extend(posts)

        result.platform_posts = platform_posts
        logger.info(f"Generated {len(platform_posts)} platform posts")

        # Save result
        self._update_progress(progress_callback, "Saving results...", 95)
        self.storage.create_content(result)

        # Mark ideas as used
        self.storage.mark_ideas_as_used([idea.id for idea in ideas])

        self._update_progress(progress_callback, "Pipeline complete!", 100)
        logger.info(f"=== Pipeline Complete: {generation_id} ===")

        return result

    def run_stage1_only(
        self,
        profile_id: str,
        num_ideas: int = 10,
        num_topics: int = 5
    ) -> List[TopicBrief]:
        """Run only Stage 1: Topic Curation."""
        logger.info("Running Stage 1 only")

        profile = self.storage.get_profile(profile_id)
        if not profile:
            raise ValueError(f"Profile not found: {profile_id}")

        ideas = self.storage.get_ideas(unused_only=True, limit=num_ideas)
        if not ideas:
            raise ValueError("No unused ideas available")

        return self.stage1.curate_topics(ideas, profile, num_topics)

    def run_stage2_only(
        self,
        topic_brief: TopicBrief,
        profile_id: str,
        versions: Optional[List[str]] = None
    ) -> List[DevelopedContent]:
        """Run only Stage 2: Content Development."""
        logger.info("Running Stage 2 only")

        profile = self.storage.get_profile(profile_id)
        if not profile:
            raise ValueError(f"Profile not found: {profile_id}")

        return self.stage2.develop_content(topic_brief, profile, versions)

    def run_stage3_only(
        self,
        content: DevelopedContent,
        profile_id: str,
        platforms: Optional[List[str]] = None
    ) -> List[PlatformPost]:
        """Run only Stage 3: Platform Optimization."""
        logger.info("Running Stage 3 only")

        profile = self.storage.get_profile(profile_id)
        if not profile:
            raise ValueError(f"Profile not found: {profile_id}")

        settings = self.storage.get_settings()
        if not settings:
            raise ValueError("User settings not configured")

        return self.stage3.optimize_for_platforms(content, profile, settings, platforms)

    def _update_progress(
        self,
        callback: Optional[callable],
        message: str,
        percent: float
    ) -> None:
        """Update progress via callback if provided."""
        if callback:
            try:
                callback(message, percent)
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")
