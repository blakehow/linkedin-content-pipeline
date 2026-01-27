"""Pipeline orchestrator - runs all three stages together."""

import logging
import uuid
import time
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

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
        idea_ids: Optional[List[str]] = None,
        existing_topics: Optional[List[TopicBrief]] = None,
        num_ideas: int = 10,
        num_topics: int = 5,
        content_versions: Optional[List[str]] = None,
        platforms: Optional[List[str]] = None,
        target_word_count: int = 1000,
        progress_callback: Optional[callable] = None
    ) -> GeneratedContent:
        """Run the complete 3-stage pipeline.

        Args:
            profile_id: Brand profile ID to use
            idea_ids: Optional list of specific idea IDs to use
            existing_topics: Optional list of existing topics to regenerate content from
            num_ideas: Number of unused ideas to pull (used if idea_ids not provided)
            num_topics: Number of topics to curate (default 5)
            content_versions: Which versions to generate (bridge, aspirational, current)
            platforms: Which platforms to optimize for (linkedin, twitter)
            target_word_count: Target word count for developed content
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

        # Get ideas: use specific IDs if provided, otherwise get unused ideas
        # Skip if using existing topics
        if existing_topics:
            ideas = []  # No ideas needed when using existing topics
            logger.info("Skipping idea loading - using existing topics")
        elif idea_ids:
            # Get specific ideas by ID
            ideas = []
            for idea_id in idea_ids:
                idea = self.storage.get_idea(idea_id)
                if idea:
                    ideas.append(idea)
                else:
                    logger.warning(f"Idea not found: {idea_id}")

            if not ideas:
                raise ValueError("None of the specified idea IDs were found.")

            logger.info(f"Using {len(ideas)} selected ideas")
        else:
            # Fallback to getting unused ideas sequentially
            ideas = self.storage.get_ideas(unused_only=True, limit=num_ideas)

            if not ideas:
                raise ValueError("No unused ideas available. Please add some ideas first.")

            logger.info(f"Using {len(ideas)} unused ideas")

        # Initialize result object
        generation_id = f"gen-{uuid.uuid4().hex[:8]}"

        # === STAGE 1: Topic Curation (or use existing topics) ===
        if existing_topics:
            # Skip stage 1 - use provided topics
            self._update_progress(progress_callback, "Using existing topics...", 15)
            logger.info("--- Using Existing Topics (Skipping Stage 1) ---")

            topic_briefs = existing_topics
            source_idea_ids = []  # No new ideas used

            # Extract source idea IDs from topics if available
            for topic in existing_topics:
                if hasattr(topic, 'source_idea_ids') and topic.source_idea_ids:
                    source_idea_ids.extend(topic.source_idea_ids)

            result = GeneratedContent(
                generation_id=generation_id,
                generation_date=datetime.now(),
                profile_id=profile_id,
                source_idea_ids=source_idea_ids,
                status=ContentStatus.DRAFT
            )

            logger.info(f"Using {len(topic_briefs)} existing topics")
        else:
            # Normal flow - curate topics from ideas
            result = GeneratedContent(
                generation_id=generation_id,
                generation_date=datetime.now(),
                profile_id=profile_id,
                source_idea_ids=[idea.id for idea in ideas],
                status=ContentStatus.DRAFT
            )

            self._update_progress(progress_callback, "Stage 1: Curating topics...", 15)
            logger.info("--- Stage 1: Topic Curation ---")

            topic_briefs = self.stage1.curate_topics(
                ideas=ideas,
                profile=profile,
                num_topics=num_topics
            )

            logger.info(f"Curated {len(topic_briefs)} topics")

        result.topic_briefs = topic_briefs

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
                versions=content_versions,
                target_word_count=target_word_count
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

        # Mark ideas as used (only if we used new ideas, not existing topics)
        if not existing_topics and ideas:
            self.storage.mark_ideas_as_used([idea.id for idea in ideas])
            logger.info(f"Marked {len(ideas)} ideas as used")

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

    def run_pipeline_progressive(
        self,
        profile_id: str,
        idea_ids: Optional[List[str]] = None,
        existing_topics: Optional[List[TopicBrief]] = None,
        num_ideas: int = 10,
        num_topics: int = 5,
        content_versions: Optional[List[str]] = None,
        platforms: Optional[List[str]] = None,
        target_word_count: int = 1000,
        progress_callback: Optional[callable] = None
    ):
        """Run pipeline progressively, yielding each content piece as it completes all stages.

        This version processes each content version through all 3 stages before moving to the next,
        providing immediate feedback instead of waiting for the entire batch to complete.

        Yields:
            Tuples of (stage, data):
            - ("topics", List[TopicBrief]) - After stage 1 completes
            - ("content", DevelopedContent) - Each content piece as it completes stages 2 & 3
            - ("complete", GeneratedContent) - Final result with all content
        """
        logger.info("=== Starting Progressive Pipeline ===")
        self._update_progress(progress_callback, "Starting pipeline...", 0)

        # Track timing
        pipeline_start = time.time()
        stage1_start = None
        stage2_start = None
        stage3_start = None
        stage1_duration = 0
        stage2_duration = 0
        stage3_duration = 0

        # Get profile and settings
        profile = self.storage.get_profile(profile_id)
        if not profile:
            raise ValueError(f"Profile not found: {profile_id}")

        settings = self.storage.get_settings()
        if not settings:
            raise ValueError("User settings not configured")

        # Track which AI provider is being used
        ai_provider = settings.ai_provider_primary if hasattr(settings, 'ai_provider_primary') else "unknown"

        # Initialize result
        generation_id = f"gen-{uuid.uuid4().hex[:8]}"

        # === STAGE 1: Topic Curation ===
        stage1_start = time.time()

        if existing_topics:
            self._update_progress(progress_callback, "Using existing topics...", 10)
            topic_briefs = existing_topics
            source_idea_ids = []
            for topic in existing_topics:
                if hasattr(topic, 'source_idea_ids') and topic.source_idea_ids:
                    source_idea_ids.extend(topic.source_idea_ids)
            ideas = []
        else:
            # Get ideas
            if idea_ids:
                ideas = []
                for idea_id in idea_ids:
                    idea = self.storage.get_idea(idea_id)
                    if idea:
                        ideas.append(idea)
                if not ideas:
                    raise ValueError("None of the specified idea IDs were found.")
            else:
                ideas = self.storage.get_ideas(unused_only=True, limit=num_ideas)
                if not ideas:
                    raise ValueError("No unused ideas available. Please add some ideas first.")

            self._update_progress(progress_callback, "Stage 1: Curating topics...", 10)
            logger.info("--- Stage 1: Topic Curation ---")

            topic_briefs = self.stage1.curate_topics(
                ideas=ideas,
                profile=profile,
                num_topics=num_topics
            )
            source_idea_ids = [idea.id for idea in ideas]

        stage1_duration = time.time() - stage1_start
        logger.info(f"Curated {len(topic_briefs)} topics in {stage1_duration:.2f}s")

        # Yield topics so UI can display them
        yield ("topics", topic_briefs)

        # Prepare for content generation
        if content_versions is None:
            content_versions = ["bridge", "aspirational", "current"]

        if platforms is None:
            if profile.platform_priority.value == "LinkedIn primary":
                platforms = ["linkedin"]
            elif profile.platform_priority.value == "Twitter primary":
                platforms = ["twitter"]
            else:
                platforms = ["linkedin", "twitter"]

        # === STAGES 2 & 3: Process each content version completely ===
        stage2_start = time.time()
        stage3_total_start = time.time()

        developed_content = []
        platform_posts = []

        total_iterations = len(topic_briefs) * len(content_versions)
        current_iteration = 0

        for topic_idx, topic in enumerate(topic_briefs):
            for version in content_versions:
                current_iteration += 1
                progress = 10 + (current_iteration / total_iterations) * 85  # 10-95%

                version_name = version.capitalize()
                self._update_progress(
                    progress_callback,
                    f"Creating {version_name} version for topic {topic_idx + 1}/{len(topic_briefs)}...",
                    progress
                )

                # Stage 2: Develop this specific version
                s2_start = time.time()
                logger.info(f"--- Developing {version} for topic: {topic.core_insight[:60]} ---")
                contents = self.stage2.develop_content(
                    topic_brief=topic,
                    profile=profile,
                    versions=[version],  # Just this one version
                    target_word_count=target_word_count
                )
                s2_elapsed = time.time() - s2_start

                # Should only be one content piece
                if contents:
                    content = contents[0]
                    content.topic_id = topic.topic_id
                    developed_content.append(content)

                    # Stage 3: Optimize for platforms immediately
                    s3_start = time.time()
                    logger.info(f"--- Optimizing {version} for platforms ---")
                    posts = self.stage3.optimize_for_platforms(
                        content=content,
                        profile=profile,
                        settings=settings,
                        platforms=platforms
                    )
                    s3_elapsed = time.time() - s3_start
                    platform_posts.extend(posts)

                    # Attach platform posts to content for display
                    content._platform_posts = posts
                    content._generation_time = s2_elapsed + s3_elapsed

                    # Yield this completed content piece immediately
                    yield ("content", content)

                    logger.info(f"Completed {version} version for topic {topic_idx + 1} in {s2_elapsed + s3_elapsed:.2f}s")

        stage2_duration = time.time() - stage2_start
        stage3_duration = time.time() - stage3_total_start - stage2_duration

        # === Save and finalize ===
        self._update_progress(progress_callback, "Saving results...", 95)

        pipeline_duration = time.time() - pipeline_start

        result = GeneratedContent(
            generation_id=generation_id,
            generation_date=datetime.now(),
            profile_id=profile_id,
            source_idea_ids=source_idea_ids,
            topic_briefs=topic_briefs,
            developed_content=developed_content,
            platform_posts=platform_posts,
            status=ContentStatus.DRAFT,
            # Timing data
            pipeline_start_time=datetime.fromtimestamp(pipeline_start),
            pipeline_end_time=datetime.now(),
            pipeline_duration_seconds=pipeline_duration,
            stage1_duration_seconds=stage1_duration,
            stage2_duration_seconds=stage2_duration,
            stage3_duration_seconds=stage3_duration,
            ai_provider_used=ai_provider
        )

        self.storage.create_content(result)

        # Mark ideas as used
        if not existing_topics and ideas:
            self.storage.mark_ideas_as_used([idea.id for idea in ideas])
            logger.info(f"Marked {len(ideas)} ideas as used")

        self._update_progress(progress_callback, "Pipeline complete!", 100)
        logger.info(f"=== Pipeline Complete: {generation_id} in {pipeline_duration:.2f}s ===")
        logger.info(f"Timing breakdown - Stage 1: {stage1_duration:.2f}s, Stage 2: {stage2_duration:.2f}s, Stage 3: {stage3_duration:.2f}s")

        # Yield final complete result
        yield ("complete", result)

    def get_estimated_runtime(
        self,
        num_topics: int = 1,
        num_versions: int = 3,
        ai_provider: Optional[str] = None
    ) -> Tuple[float, Dict[str, Any]]:
        """Estimate pipeline runtime based on historical data.

        Args:
            num_topics: Number of topics to generate
            num_versions: Number of content versions per topic
            ai_provider: AI provider to use (for provider-specific estimates)

        Returns:
            Tuple of (estimated_seconds, stats_dict)
        """
        # Get recent pipeline runs with timing data
        all_content = self.storage.get_all_content()

        # Filter to only runs with timing data
        timed_runs = [
            c for c in all_content
            if hasattr(c, 'pipeline_duration_seconds') and c.pipeline_duration_seconds is not None
        ]

        if not timed_runs:
            # No historical data - use rough estimates
            # Gemini: ~5-10s per content piece
            # Ollama: ~15-30s per content piece
            if ai_provider == "ollama":
                est_per_piece = 22.5  # midpoint of 15-30
            else:
                est_per_piece = 7.5  # midpoint of 5-10

            total_pieces = num_topics * num_versions
            estimated_total = 10 + (total_pieces * est_per_piece)  # +10s for topic curation

            return estimated_total, {
                "source": "default_estimates",
                "sample_size": 0,
                "confidence": "low"
            }

        # Filter by AI provider if specified
        if ai_provider:
            provider_runs = [
                c for c in timed_runs
                if hasattr(c, 'ai_provider_used') and c.ai_provider_used == ai_provider
            ]
            if provider_runs:
                timed_runs = provider_runs

        # Use most recent 10 runs
        recent_runs = sorted(timed_runs, key=lambda x: x.generation_date, reverse=True)[:10]

        # Calculate average time per content piece
        avg_stage1 = sum(c.stage1_duration_seconds or 0 for c in recent_runs) / len(recent_runs)
        avg_stage2 = sum(c.stage2_duration_seconds or 0 for c in recent_runs) / len(recent_runs)
        avg_stage3 = sum(c.stage3_duration_seconds or 0 for c in recent_runs) / len(recent_runs)

        # Calculate average content pieces per run
        avg_pieces_per_run = sum(len(c.developed_content) for c in recent_runs) / len(recent_runs)

        if avg_pieces_per_run > 0:
            avg_time_per_piece = (avg_stage2 + avg_stage3) / avg_pieces_per_run
        else:
            avg_time_per_piece = 10  # fallback

        # Estimate for requested configuration
        total_pieces = num_topics * num_versions
        estimated_total = avg_stage1 + (total_pieces * avg_time_per_piece)

        return estimated_total, {
            "source": "historical_data",
            "sample_size": len(recent_runs),
            "confidence": "high" if len(recent_runs) >= 5 else "medium",
            "avg_stage1": avg_stage1,
            "avg_per_piece": avg_time_per_piece,
            "provider": ai_provider or "mixed"
        }

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
