"""Data storage layer with mock implementation."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from src.data.models import (
    Idea,
    BrandProfile,
    UserSettings,
    GeneratedContent,
    PromptTemplate,
    ContentPerformance,
)
from config.settings import DATA_DIR


class MockStorage:
    """Mock storage using local JSON files."""

    def __init__(self, data_dir: Path = DATA_DIR):
        """Initialize mock storage."""
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # File paths
        self.ideas_file = self.data_dir / "ideas.json"
        self.profiles_file = self.data_dir / "brand_profiles.json"
        self.settings_file = self.data_dir / "user_settings.json"
        self.content_file = self.data_dir / "generated_content.json"
        self.prompts_file = self.data_dir / "prompt_templates.json"
        self.performance_file = self.data_dir / "content_performance.json"

        # Initialize files if they don't exist
        self._init_file(self.ideas_file, [])
        self._init_file(self.profiles_file, [])
        self._init_file(self.settings_file, None)
        self._init_file(self.content_file, [])
        self._init_file(self.prompts_file, [])
        self._init_file(self.performance_file, [])

    def _init_file(self, file_path: Path, default_data: Any) -> None:
        """Initialize a JSON file if it doesn't exist."""
        if not file_path.exists():
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=2, default=str)

    def _load_json(self, file_path: Path) -> Any:
        """Load data from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_json(self, file_path: Path, data: Any) -> None:
        """Save data to JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)

    # ========================================================================
    # Ideas
    # ========================================================================

    def create_idea(self, idea: Idea) -> Idea:
        """Create a new idea."""
        ideas = self._load_json(self.ideas_file)
        ideas.append(idea.model_dump(mode='json'))
        self._save_json(self.ideas_file, ideas)
        return idea

    def get_ideas(self, unused_only: bool = False, limit: Optional[int] = None) -> List[Idea]:
        """Get all ideas."""
        ideas_data = self._load_json(self.ideas_file)
        ideas = [Idea(**data) for data in ideas_data]

        if unused_only:
            ideas = [idea for idea in ideas if not idea.used]

        # Sort by timestamp, newest first
        ideas.sort(key=lambda x: x.timestamp, reverse=True)

        if limit:
            ideas = ideas[:limit]

        return ideas

    def get_idea(self, idea_id: str) -> Optional[Idea]:
        """Get a specific idea by ID."""
        ideas = self.get_ideas()
        for idea in ideas:
            if idea.id == idea_id:
                return idea
        return None

    def update_idea(self, idea: Idea) -> Idea:
        """Update an existing idea."""
        ideas_data = self._load_json(self.ideas_file)
        for i, data in enumerate(ideas_data):
            if data['id'] == idea.id:
                ideas_data[i] = idea.model_dump(mode='json')
                break
        self._save_json(self.ideas_file, ideas_data)
        return idea

    def delete_idea(self, idea_id: str) -> bool:
        """Delete an idea."""
        ideas_data = self._load_json(self.ideas_file)
        original_len = len(ideas_data)
        ideas_data = [data for data in ideas_data if data['id'] != idea_id]

        if len(ideas_data) < original_len:
            self._save_json(self.ideas_file, ideas_data)
            return True
        return False

    def mark_ideas_as_used(self, idea_ids: List[str]) -> None:
        """Mark multiple ideas as used."""
        ideas_data = self._load_json(self.ideas_file)
        now = datetime.now()

        for data in ideas_data:
            if data['id'] in idea_ids:
                data['used'] = True
                data['used_date'] = now.isoformat()

        self._save_json(self.ideas_file, ideas_data)

    # ========================================================================
    # Brand Profiles
    # ========================================================================

    def create_profile(self, profile: BrandProfile) -> BrandProfile:
        """Create a new brand profile."""
        profiles = self._load_json(self.profiles_file)
        profiles.append(profile.model_dump(mode='json'))
        self._save_json(self.profiles_file, profiles)
        return profile

    def get_profiles(self, active_only: bool = True) -> List[BrandProfile]:
        """Get all brand profiles."""
        profiles_data = self._load_json(self.profiles_file)
        profiles = [BrandProfile(**data) for data in profiles_data]

        if active_only:
            profiles = [p for p in profiles if p.is_active]

        return profiles

    def get_profile(self, profile_id: str) -> Optional[BrandProfile]:
        """Get a specific profile by ID."""
        profiles = self.get_profiles(active_only=False)
        for profile in profiles:
            if profile.profile_id == profile_id:
                return profile
        return None

    def update_profile(self, profile: BrandProfile) -> BrandProfile:
        """Update an existing profile."""
        profiles_data = self._load_json(self.profiles_file)
        for i, data in enumerate(profiles_data):
            if data['profile_id'] == profile.profile_id:
                profiles_data[i] = profile.model_dump(mode='json')
                break
        self._save_json(self.profiles_file, profiles_data)
        return profile

    def delete_profile(self, profile_id: str) -> bool:
        """Delete a brand profile."""
        profiles_data = self._load_json(self.profiles_file)
        original_len = len(profiles_data)
        profiles_data = [data for data in profiles_data if data['profile_id'] != profile_id]

        if len(profiles_data) < original_len:
            self._save_json(self.profiles_file, profiles_data)
            return True
        return False

    # ========================================================================
    # User Settings
    # ========================================================================

    def get_settings(self) -> Optional[UserSettings]:
        """Get user settings."""
        settings_data = self._load_json(self.settings_file)
        if settings_data:
            return UserSettings(**settings_data)
        return None

    def save_settings(self, settings: UserSettings) -> UserSettings:
        """Save user settings."""
        self._save_json(self.settings_file, settings.model_dump(mode='json'))
        return settings

    # ========================================================================
    # Generated Content
    # ========================================================================

    def create_content(self, content: GeneratedContent) -> GeneratedContent:
        """Save generated content."""
        content_data = self._load_json(self.content_file)
        content_data.append(content.model_dump(mode='json'))
        self._save_json(self.content_file, content_data)
        return content

    def get_content_list(self, limit: Optional[int] = None) -> List[GeneratedContent]:
        """Get all generated content."""
        content_data = self._load_json(self.content_file)
        content = [GeneratedContent(**data) for data in content_data]

        # Sort by generation date, newest first
        content.sort(key=lambda x: x.generation_date, reverse=True)

        if limit:
            content = content[:limit]

        return content

    def get_content(self, generation_id: str) -> Optional[GeneratedContent]:
        """Get specific generated content by ID."""
        content_list = self.get_content_list()
        for content in content_list:
            if content.generation_id == generation_id:
                return content
        return None

    def update_content(self, content: GeneratedContent) -> GeneratedContent:
        """Update generated content."""
        content_data = self._load_json(self.content_file)
        for i, data in enumerate(content_data):
            if data['generation_id'] == content.generation_id:
                content_data[i] = content.model_dump(mode='json')
                break
        self._save_json(self.content_file, content_data)
        return content

    # ========================================================================
    # Prompt Templates
    # ========================================================================

    def create_prompt(self, prompt: PromptTemplate) -> PromptTemplate:
        """Create a new prompt template."""
        prompts = self._load_json(self.prompts_file)
        prompts.append(prompt.model_dump(mode='json'))
        self._save_json(self.prompts_file, prompts)
        return prompt

    def get_prompts(self, stage: Optional[int] = None) -> List[PromptTemplate]:
        """Get prompt templates, optionally filtered by stage."""
        prompts_data = self._load_json(self.prompts_file)
        prompts = [PromptTemplate(**data) for data in prompts_data]

        if stage is not None:
            prompts = [p for p in prompts if p.stage == stage]

        return prompts

    def get_default_prompt(self, stage: int) -> Optional[PromptTemplate]:
        """Get the default prompt for a stage."""
        prompts = self.get_prompts(stage=stage)
        for prompt in prompts:
            if prompt.is_default:
                return prompt
        # Return first if no default
        return prompts[0] if prompts else None

    def update_prompt(self, prompt: PromptTemplate) -> PromptTemplate:
        """Update a prompt template."""
        prompts_data = self._load_json(self.prompts_file)
        for i, data in enumerate(prompts_data):
            if data['template_id'] == prompt.template_id:
                prompts_data[i] = prompt.model_dump(mode='json')
                break
        self._save_json(self.prompts_file, prompts_data)
        return prompt

    # ========================================================================
    # Analytics
    # ========================================================================

    def save_performance(self, performance: ContentPerformance) -> ContentPerformance:
        """Save content performance data."""
        perf_data = self._load_json(self.performance_file)

        # Update if exists, otherwise append
        found = False
        for i, data in enumerate(perf_data):
            if data['post_id'] == performance.post_id:
                perf_data[i] = performance.model_dump(mode='json')
                found = True
                break

        if not found:
            perf_data.append(performance.model_dump(mode='json'))

        self._save_json(self.performance_file, perf_data)
        return performance

    def get_performance(self, post_id: Optional[str] = None) -> List[ContentPerformance]:
        """Get performance data."""
        perf_data = self._load_json(self.performance_file)
        performance = [ContentPerformance(**data) for data in perf_data]

        if post_id:
            performance = [p for p in performance if p.post_id == post_id]

        return performance


# Global storage instance
_storage: Optional[MockStorage] = None


def get_storage() -> MockStorage:
    """Get the storage instance."""
    global _storage
    if _storage is None:
        _storage = MockStorage()
    return _storage
