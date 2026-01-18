"""Load sample data for demo purposes."""

import uuid
from datetime import datetime, timedelta

from src.data.models import (
    Idea, BrandProfile, UserSettings,
    ProfileType, PlatformPriority, EmojiUsage
)
from src.data.storage import get_storage


def load_sample_data():
    """Load sample data into the storage."""

    print("Loading sample data...")
    storage = get_storage()

    # === User Settings ===
    print("Creating user settings...")
    settings = UserSettings(
        user_full_name="Alex Johnson",
        linkedin_username="alexjohnson",
        twitter_username="@alexj",
        notification_email="alex@example.com",
        content_tone_default="Professional & Friendly",
        emoji_usage=EmojiUsage.MODERATE,
        include_hashtags=True,
        max_hashtags=5,
        auto_post_enabled=False
    )
    storage.save_settings(settings)

    # === Brand Profiles ===
    print("Creating brand profiles...")

    profile1 = BrandProfile(
        profile_id=f"profile-{uuid.uuid4().hex[:8]}",
        profile_name="Personal Brand",
        profile_type=ProfileType.PERSONAL,
        linkedin_username="alexjohnson",
        twitter_username="@alexj",
        target_audience="Tech professionals, founders, and leaders navigating growth challenges",
        tone="Authentic, vulnerable, insightful - balancing personal stories with tactical advice",
        key_topics=["Leadership", "Team Management", "AI & Technology", "Personal Growth"],
        platform_priority=PlatformPriority.LINKEDIN_PRIMARY,
        bio="Helping tech leaders scale their teams and build better systems. Former CTO, current founder. Learning in public about leadership, AI, and sustainable growth.",
        is_active=True,
        created_at=datetime.now()
    )
    storage.create_profile(profile1)

    settings.active_profile_id = profile1.profile_id
    storage.save_settings(settings)

    profile2 = BrandProfile(
        profile_id=f"profile-{uuid.uuid4().hex[:8]}",
        profile_name="Company Brand",
        profile_type=ProfileType.COMPANY,
        linkedin_username="techcompany",
        twitter_username="@techco",
        target_audience="B2B decision makers, operations leaders, scaling companies",
        tone="Professional, authoritative, data-driven",
        key_topics=["Product Development", "Operations", "Customer Success", "Industry Insights"],
        platform_priority=PlatformPriority.BOTH_EQUAL,
        bio="We help companies scale operations and build high-performing teams. Sharing insights on modern work, AI tools, and operational excellence.",
        is_active=False,
        created_at=datetime.now()
    )
    storage.create_profile(profile2)

    # === Sample Ideas ===
    print("Creating sample ideas...")

    sample_ideas = [
        {
            "text": "Noticed our team was having too many meetings. Calendar was packed but actual work wasn't getting done. Realized synchronous time needs to be protected, not defaulted to. Started experimenting with async-first communication.",
            "category": "Team Management"
        },
        {
            "text": "Had a conversation with a founder struggling to delegate. They said 'it's faster if I just do it myself.' But that's exactly the problem - short-term speed, long-term bottleneck. Delegation isn't about speed, it's about scale.",
            "category": "Leadership"
        },
        {
            "text": "Spent 3 hours debugging an issue that could have been prevented with 10 minutes of documentation. The ROI on good docs is insane, but we always deprioritize it because it's not 'urgent.'",
            "category": "Operations"
        },
        {
            "text": "Watched a junior dev ask a 'stupid' question that revealed a huge gap in our onboarding. Sometimes the best insights come from beginners who don't yet know what they're 'supposed' to know.",
            "category": "Team Management"
        },
        {
            "text": "Tried ChatGPT for brainstorming and was blown away. Not because it had all the answers, but because it asked questions I hadn't considered. AI as a thinking partner, not a replacement.",
            "category": "AI & Technology"
        },
        {
            "text": "Read a post about 'shipping fast' vs 'shipping right.' Realized we've been optimizing for speed without considering the cost of technical debt. Sometimes slow is faster.",
            "category": "Product Development"
        },
        {
            "text": "Had to fire someone for the first time. Hardest conversation I've ever had. Learned that delaying hard decisions is just transferring pain to your future self - and being unfair to the person.",
            "category": "Leadership"
        },
        {
            "text": "Our best hire this year came from an 'unconventional' background. They didn't check the boxes on paper but had the right mindset. Reminded me that hiring for potential beats hiring for experience.",
            "category": "Team Management"
        },
        {
            "text": "Realized I was burning out not from working too much, but from context switching too much. 8 hours of fragmented work is exhausting. 4 hours of deep work is energizing.",
            "category": "Personal Growth"
        },
        {
            "text": "Customer churn analysis revealed our best customers weren't using our fanciest features. They loved the basics done well. Feature bloat is a trap.",
            "category": "Product Development"
        },
        {
            "text": "Started writing more and noticed my thinking got clearer. Writing forces you to organize fuzzy thoughts into coherent arguments. It's thinking tool-assisted.",
            "category": "Personal Growth"
        },
        {
            "text": "Implemented a 'no meeting Wednesday' policy. Productivity skyrocketed. The hardest part wasn't the policy - it was defending it when people wanted exceptions.",
            "category": "Operations"
        }
    ]

    for i, idea_data in enumerate(sample_ideas):
        idea = Idea(
            id=f"idea-{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now() - timedelta(days=len(sample_ideas) - i),
            text=idea_data["text"],
            category=idea_data["category"],
            source="Demo Data",
            used=i < 5  # Mark first 5 as used
        )

        if idea.used:
            idea.used_date = datetime.now() - timedelta(days=2)

        storage.create_idea(idea)

    print("Sample data loaded successfully!")
    print("   - User settings configured")
    print(f"   - {len([profile1, profile2])} brand profiles created")
    print(f"   - {len(sample_ideas)} sample ideas added")
    print("\nYou can now run: streamlit run app.py")


if __name__ == "__main__":
    load_sample_data()
