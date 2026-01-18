# Testing Plan & Quality Assurance

## Testing Strategy Overview

Comprehensive testing coverage across all components with focus on security, reliability, and user experience.

---

## Testing Pyramid

```
         /\
        /  \  E2E Tests (5%)
       /----\  Integration Tests (25%)
      /------\  Unit Tests (70%)
     /--------\
```

---

## 1. Unit Tests (70% Coverage)

### Google Sheets Operations
**File:** `tests/test_google_sheets.py`

```python
def test_connect_to_sheet():
    """Test successful connection to Google Sheets"""

def test_read_ideas_from_sheet():
    """Test reading ideas with various data types"""

def test_write_idea_to_sheet():
    """Test writing new idea with validation"""

def test_update_idea_status():
    """Test marking idea as used"""

def test_read_settings():
    """Test loading user settings"""

def test_update_settings():
    """Test saving updated settings"""

def test_load_brand_profiles():
    """Test loading all brand profiles"""

def test_handle_missing_sheet():
    """Test error handling for missing sheet"""

def test_handle_invalid_credentials():
    """Test error handling for auth failure"""

def test_handle_rate_limiting():
    """Test retry logic for rate limits"""
```

### AI/LLM Integration
**File:** `tests/test_ai.py`

```python
def test_ollama_connection():
    """Test connection to local Ollama service"""

def test_generate_with_ollama():
    """Test content generation with Ollama"""

def test_handle_ollama_timeout():
    """Test timeout handling"""

def test_handle_ollama_out_of_memory():
    """Test OOM error handling"""

def test_gemini_fallback():
    """Test fallback to Gemini API"""

def test_prompt_injection_protection():
    """Test that malicious prompts are sanitized"""

def test_output_validation():
    """Test that AI output meets expected format"""

def test_token_limit_handling():
    """Test handling of context length limits"""
```

### Pipeline Stages
**File:** `tests/test_pipeline.py`

```python
# Stage 1: Topic Curation
def test_stage1_curate_topics():
    """Test topic curation from ideas"""

def test_stage1_no_ideas_available():
    """Test handling of empty ideas list"""

def test_stage1_insufficient_ideas():
    """Test handling of < 5 ideas"""

# Stage 2: Content Development
def test_stage2_develop_content():
    """Test content development for all versions"""

def test_stage2_web_research():
    """Test web research for statistics"""

def test_stage2_citation_formatting():
    """Test proper source citations"""

def test_stage2_version_differences():
    """Test that A/B/C versions are distinct"""

# Stage 3: Platform Optimization
def test_stage3_linkedin_optimization():
    """Test LinkedIn post formatting"""

def test_stage3_twitter_thread_creation():
    """Test Twitter thread generation"""

def test_stage3_character_limits():
    """Test adherence to platform limits"""

def test_stage3_hashtag_generation():
    """Test hashtag relevance and count"""
```

### Data Models
**File:** `tests/test_models.py`

```python
def test_user_settings_validation():
    """Test UserSettings model validation"""

def test_brand_profile_validation():
    """Test BrandProfile model validation"""

def test_idea_model_validation():
    """Test Idea model validation"""

def test_generated_content_validation():
    """Test GeneratedContent model validation"""

def test_invalid_email_rejected():
    """Test email validation"""

def test_invalid_timezone_rejected():
    """Test timezone validation"""

def test_invalid_url_rejected():
    """Test URL validation"""
```

### Utilities
**File:** `tests/test_utils.py`

```python
def test_sanitize_input():
    """Test input sanitization"""

def test_format_timestamp():
    """Test timestamp formatting"""

def test_validate_credentials():
    """Test credential validation"""

def test_mask_sensitive_data():
    """Test masking of API keys in logs"""
```

---

## 2. Integration Tests (25% Coverage)

### End-to-End Pipeline
**File:** `tests/integration/test_pipeline_e2e.py`

```python
def test_full_pipeline_execution():
    """Test complete pipeline from ideas to posts"""
    # 1. Add ideas to sheet
    # 2. Run Stage 1 (Curation)
    # 3. Run Stage 2 (Development)
    # 4. Run Stage 3 (Optimization)
    # 5. Verify output quality

def test_pipeline_with_different_profiles():
    """Test pipeline with Personal, Company, Product profiles"""

def test_pipeline_error_recovery():
    """Test pipeline continues after non-critical errors"""

def test_pipeline_state_persistence():
    """Test resuming pipeline after interruption"""
```

### Google Sheets Integration
**File:** `tests/integration/test_sheets_integration.py`

```python
def test_round_trip_idea_storage():
    """Test write then read idea from sheets"""

def test_concurrent_sheet_access():
    """Test multiple simultaneous reads/writes"""

def test_large_dataset_handling():
    """Test with 1000+ ideas"""

def test_sheet_quota_handling():
    """Test behavior near API quota limits"""
```

### AI Service Integration
**File:** `tests/integration/test_ai_integration.py`

```python
def test_ollama_real_content_generation():
    """Test real content generation with Ollama"""

def test_gemini_real_content_generation():
    """Test real content generation with Gemini"""

def test_ai_service_failover():
    """Test fallback from Ollama to Gemini"""

def test_long_running_generation():
    """Test 5+ minute generation tasks"""
```

---

## 3. End-to-End Tests (5% Coverage)

### User Workflows
**File:** `tests/e2e/test_user_workflows.py`

```python
def test_first_time_setup():
    """Test complete first-time user setup flow"""

def test_add_idea_and_generate_content():
    """Test adding idea and running full pipeline"""

def test_review_and_schedule_post():
    """Test content review and scheduling"""

def test_switch_between_profiles():
    """Test switching between different brand profiles"""

def test_export_import_settings():
    """Test settings export/import workflow"""
```

### UI Tests (Streamlit)
**File:** `tests/e2e/test_ui.py`

```python
def test_streamlit_app_loads():
    """Test app starts without errors"""

def test_navigation_between_pages():
    """Test all pages load correctly"""

def test_settings_page_functionality():
    """Test settings page CRUD operations"""

def test_idea_entry_form():
    """Test idea entry form submission"""

def test_content_review_page():
    """Test content review and editing"""

def test_analytics_page():
    """Test analytics display"""
```

---

## 4. Security Tests

### Authentication & Authorization
**File:** `tests/security/test_auth.py`

```python
def test_google_oauth_flow():
    """Test OAuth flow for Google Sheets"""

def test_credentials_not_exposed():
    """Test credentials not in logs or errors"""

def test_session_management():
    """Test secure session handling"""

def test_unauthorized_sheet_access():
    """Test error on accessing sheet without permission"""
```

### Input Validation
**File:** `tests/security/test_input_validation.py`

```python
def test_xss_protection():
    """Test XSS prevention in user inputs"""

def test_sql_injection_protection():
    """Test SQL injection prevention (if using SQL)"""

def test_command_injection_protection():
    """Test command injection prevention"""

def test_path_traversal_protection():
    """Test file path validation"""

def test_prompt_injection_protection():
    """Test AI prompt injection prevention"""

def test_malicious_file_upload():
    """Test file upload validation"""
```

### Data Protection
**File:** `tests/security/test_data_protection.py`

```python
def test_sensitive_data_encryption():
    """Test API keys stored securely"""

def test_pii_handling():
    """Test PII is not logged or exposed"""

def test_data_sanitization():
    """Test output sanitization"""

def test_secure_api_communication():
    """Test HTTPS for external APIs"""
```

---

## 5. Performance Tests

### Load Testing
**File:** `tests/performance/test_load.py`

```python
def test_handle_100_ideas():
    """Test pipeline with 100 ideas"""

def test_handle_1000_ideas():
    """Test pipeline with 1000 ideas"""

def test_concurrent_users():
    """Test 10 simultaneous users (if multi-tenant)"""

def test_large_content_generation():
    """Test generating 50 posts at once"""
```

### Response Time Tests
**File:** `tests/performance/test_response_times.py`

```python
def test_idea_submission_speed():
    """Test idea submission < 2 seconds"""

def test_settings_load_speed():
    """Test settings load < 1 second"""

def test_pipeline_stage1_speed():
    """Test Stage 1 completes < 30 seconds"""

def test_pipeline_stage2_speed():
    """Test Stage 2 completes < 2 minutes"""

def test_pipeline_stage3_speed():
    """Test Stage 3 completes < 30 seconds"""
```

---

## 6. Compatibility Tests

### Browser Compatibility (for Streamlit UI)
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

### OS Compatibility
- Windows 10/11
- macOS (latest 2 versions)
- Linux (Ubuntu 20.04+)

### Python Version Compatibility
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

---

## Test Data & Fixtures

### Sample Ideas
**File:** `tests/fixtures/sample_ideas.json`
```json
[
  {
    "id": "test-001",
    "text": "Noticed our team struggles with async communication...",
    "category": "Team Management",
    "source": "Test"
  }
]
```

### Sample Settings
**File:** `tests/fixtures/sample_settings.json`

### Sample Brand Profiles
**File:** `tests/fixtures/sample_profiles.json`

### Mock API Responses
**File:** `tests/fixtures/mock_api_responses.json`

---

## Automated Testing Pipeline

### Pre-Commit Hooks
```bash
# .pre-commit-config.yaml
- Run linting (flake8, black)
- Run type checking (mypy)
- Run fast unit tests (< 10s)
```

### CI/CD Pipeline (GitHub Actions)
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11, 3.12]

    steps:
      - Checkout code
      - Setup Python
      - Install dependencies
      - Run linting
      - Run type checking
      - Run unit tests
      - Run integration tests
      - Run security scans
      - Generate coverage report
      - Upload coverage to Codecov
```

---

## Test Coverage Requirements

### Minimum Coverage Targets
- Overall code coverage: **80%**
- Critical paths (auth, data storage): **95%**
- UI code: **60%**
- Utility functions: **90%**

### Coverage Report
```bash
pytest --cov=src --cov-report=html --cov-report=term
```

---

## Manual Testing Checklist

### Setup & Installation
- [ ] Fresh install on Windows
- [ ] Fresh install on macOS
- [ ] Fresh install on Linux
- [ ] Install with Ollama
- [ ] Install with Gemini API
- [ ] First-time setup wizard completion

### Core Features
- [ ] Add idea via UI
- [ ] View all ideas
- [ ] Edit existing idea
- [ ] Delete idea
- [ ] Run pipeline (Stage 1)
- [ ] Run pipeline (Stage 2)
- [ ] Run pipeline (Stage 3)
- [ ] Run full pipeline
- [ ] Review generated content
- [ ] Edit generated content
- [ ] Schedule post
- [ ] Publish post manually

### Settings & Configuration
- [ ] Update user settings
- [ ] Create new brand profile
- [ ] Edit brand profile
- [ ] Switch between profiles
- [ ] Export settings
- [ ] Import settings
- [ ] Test API connections

### Error Handling
- [ ] Invalid Google Sheets ID
- [ ] Missing Ollama service
- [ ] Invalid API credentials
- [ ] Network disconnection
- [ ] Out of memory error
- [ ] Rate limit exceeded

### Cross-Browser (Streamlit UI)
- [ ] All features work in Chrome
- [ ] All features work in Firefox
- [ ] All features work in Safari
- [ ] All features work in Edge

---

## Bug Tracking & Reporting

### Issue Template
```markdown
**Bug Description:**
[Clear description]

**Steps to Reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Environment:**
- OS: [Windows/macOS/Linux]
- Python version: [3.x]
- App version: [1.0.0]
- AI service: [Ollama/Gemini]

**Screenshots/Logs:**
[Attach relevant files]
```

---

## Test Automation Tools

```
# Testing
pytest==7.4.0                  # Test framework
pytest-cov==4.1.0              # Coverage reporting
pytest-mock==3.11.1            # Mocking
pytest-asyncio==0.21.0         # Async testing

# Code Quality
flake8==6.0.0                  # Linting
black==23.7.0                  # Code formatting
mypy==1.4.1                    # Type checking
isort==5.12.0                  # Import sorting

# Security
bandit==1.7.5                  # Security linting
safety==2.3.5                  # Dependency vulnerability scan

# Performance
pytest-benchmark==4.0.0        # Performance benchmarking
locust==2.15.1                 # Load testing
```

---

## Testing Best Practices

1. **Write tests first (TDD)** for critical features
2. **Use fixtures** for common test data
3. **Mock external services** (APIs, databases)
4. **Test edge cases** and error conditions
5. **Keep tests fast** (unit tests < 1s each)
6. **Use descriptive test names** (`test_user_can_add_idea_with_emoji`)
7. **One assertion per test** when possible
8. **Clean up after tests** (delete test data)
9. **Run tests before commits**
10. **Maintain test documentation**

---

Ready to proceed with security audit checklist?
