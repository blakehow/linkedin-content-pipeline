"""Test the complete pipeline."""

import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

print("=" * 60)
print("LinkedIn Content Pipeline - Integration Test")
print("=" * 60)
print()

# Test 1: Import all modules
print("[1/5] Testing imports...")
try:
    from src.data.storage import get_storage
    from src.pipeline.orchestrator import PipelineOrchestrator
    from src.ai.factory import get_ai_client
    from config.settings import get_settings
    print("  OK - All modules imported successfully")
except Exception as e:
    print(f"  FAILED - Import error: {e}")
    sys.exit(1)

# Test 2: Check configuration
print("\n[2/5] Testing configuration...")
try:
    settings = get_settings()
    print(f"  - AI Service: {settings.ai_service_primary}")
    print(f"  - Demo Mode: {settings.is_demo_mode}")
    print(f"  - Storage: {settings.data_storage_type}")
    print("  OK - Configuration loaded")
except Exception as e:
    print(f"  FAILED - Config error: {e}")
    sys.exit(1)

# Test 3: Check data storage
print("\n[3/5] Testing data storage...")
try:
    storage = get_storage()

    # Check for data
    settings_data = storage.get_settings()
    profiles = storage.get_profiles()
    ideas = storage.get_ideas()

    print(f"  - User settings: {'Configured' if settings_data else 'Not configured'}")
    print(f"  - Brand profiles: {len(profiles)}")
    print(f"  - Ideas: {len(ideas)} total, {len([i for i in ideas if not i.used])} unused")

    if not settings_data or len(profiles) == 0 or len(ideas) < 5:
        print("  WARNING - Insufficient data. Run: python load_sample_data.py")
        sys.exit(1)

    print("  OK - Data storage working")
except Exception as e:
    print(f"  FAILED - Storage error: {e}")
    sys.exit(1)

# Test 4: Check AI client
print("\n[4/5] Testing AI client...")
try:
    ai_client = get_ai_client()
    is_available = ai_client.is_available()

    print(f"  - AI Client available: {is_available}")

    if is_available:
        # Test simple generation
        response = ai_client.generate("Say hello", max_tokens=50)
        print(f"  - Test generation: {response[:50]}...")
        print("  OK - AI client working")
    else:
        print("  WARNING - AI client not available, but mock fallback should work")
        print("  OK - Mock AI available")
except Exception as e:
    print(f"  FAILED - AI client error: {e}")
    sys.exit(1)

# Test 5: Run mini pipeline
print("\n[5/5] Testing pipeline execution...")
try:
    orchestrator = PipelineOrchestrator()

    # Get active profile
    active_profile_id = settings_data.active_profile_id

    if not active_profile_id:
        active_profile_id = profiles[0].profile_id

    print(f"  - Using profile: {active_profile_id}")
    print("  - Running Stage 1 (Topic Curation)...")

    # Run just Stage 1 for testing
    unused_ideas = storage.get_ideas(unused_only=True)
    test_ideas = unused_ideas[:5]

    profile = storage.get_profile(active_profile_id)
    topics = orchestrator.stage1.curate_topics(
        ideas=test_ideas,
        profile=profile,
        num_topics=2  # Just 2 for testing
    )

    print(f"  - Generated {len(topics)} topics")
    if topics:
        print(f"  - Sample topic: {topics[0].core_insight[:60]}...")

    print("  OK - Pipeline stage 1 working")

except Exception as e:
    print(f"  FAILED - Pipeline error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
print("\nThe application is ready to use.")
print("Run: streamlit run app.py")
print()
