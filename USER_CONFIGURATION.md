# User Configuration Management

## Overview

All user-specific settings are configurable through the Streamlit UI and saved persistently. This allows multiple users to run the app with their own settings without editing code.

---

## Two-Tier Configuration System

### Tier 1: Sensitive Credentials (Local .env)
**Storage:** `.env` file (never committed to git)
**Contains:** API keys, passwords, tokens
**Edited:** Manually or via secure settings UI

### Tier 2: User Preferences (Google Sheets)
**Storage:** "Settings" tab in Google Sheet
**Contains:** Usernames, profile settings, preferences
**Edited:** Through Streamlit UI

---

## Google Sheets Configuration

### New Tab: "Settings"

| Setting_Key | Setting_Value | Category | Description |
|------------|---------------|----------|-------------|
| `linkedin_username` | `john_doe` | Social | Your LinkedIn profile username |
| `twitter_username` | `@johndoe` | Social | Your Twitter/X handle |
| `user_full_name` | `John Doe` | Profile | Your full name for attribution |
| `default_timezone` | `America/New_York` | General | Timezone for scheduling |
| `content_tone_default` | `Professional & Friendly` | Content | Default writing tone |
| `auto_post_enabled` | `FALSE` | Publishing | Auto-post or manual review |
| `linkedin_post_frequency` | `3` | Publishing | Posts per week |
| `twitter_post_frequency` | `5` | Publishing | Tweets per week |
| `preferred_post_times` | `09:00,13:00,17:00` | Publishing | Best times to post (24hr) |
| `include_hashtags` | `TRUE` | Content | Add hashtags to posts |
| `max_hashtags` | `5` | Content | Maximum hashtags per post |
| `emoji_usage` | `Moderate` | Content | None/Light/Moderate/Heavy |
| `notification_email` | `john@example.com` | Notifications | Email for alerts |

### New Tab: "Brand_Profiles"

Replaces "Audience_Profiles" with more detailed brand/persona configurations:

| Profile_ID | Profile_Name | Profile_Type | LinkedIn_Username | Twitter_Username | Target_Audience | Tone | Key_Topics | Platform_Priority | Bio | Avatar_URL |
|------------|--------------|--------------|-------------------|------------------|-----------------|------|------------|-------------------|-----|------------|
| `personal_001` | Personal Brand | Personal | `john_doe` | `@johndoe` | Tech professionals, founders | Authentic, vulnerable, insightful | Leadership, AI, startups | LinkedIn primary | Helping founders scale... | url |
| `company_001` | Company Brand | Company | `company_page` | `@company` | B2B decision makers | Professional, authoritative | Product, industry insights | Both equal | We help companies... | url |
| `product_001` | Product Brand | Product | `product_page` | `@product` | Users, potential customers | Helpful, educational | Features, tutorials, tips | Twitter primary | The best tool for... | url |

---

## Streamlit Settings UI

### Settings Page Structure

**Tab 1: Profile Settings**
- Full name
- Email for notifications
- Timezone selection (dropdown)
- Profile photo upload

**Tab 2: Social Media Accounts**
- LinkedIn username/profile URL
- Twitter/X handle
- Option to add more platforms
- Test connection buttons

**Tab 3: Content Preferences**
- Default tone selector (dropdown)
- Emoji usage level (slider)
- Hashtag preferences (toggles)
- Max hashtags (number input)

**Tab 4: Publishing Settings**
- Auto-post enabled (toggle)
- Post frequency per platform (sliders)
- Preferred posting times (time pickers)
- Review before posting (toggle)

**Tab 5: Brand Profiles**
- View all profiles (data table)
- Add new profile (form)
- Edit existing profile (modal)
- Set default/active profile

**Tab 6: API Credentials**
- Google Sheets (connection status + re-auth button)
- Twitter API (add/edit credentials, test connection)
- LinkedIn API (add/edit credentials if using)
- Ollama (connection status, model selection)

---

## Configuration Data Models

### User Settings Model
```python
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import time

class UserSettings(BaseModel):
    # Profile
    linkedin_username: str
    twitter_username: str
    user_full_name: str
    notification_email: EmailStr
    default_timezone: str = "UTC"

    # Content Preferences
    content_tone_default: str = "Professional & Friendly"
    emoji_usage: str = "Moderate"  # None, Light, Moderate, Heavy
    include_hashtags: bool = True
    max_hashtags: int = 5

    # Publishing
    auto_post_enabled: bool = False
    linkedin_post_frequency: int = 3  # per week
    twitter_post_frequency: int = 5  # per week
    preferred_post_times: List[time] = []

    # Notifications
    enable_email_notifications: bool = True
    notify_on_post: bool = True
    notify_on_engagement: bool = False
```

### Brand Profile Model
```python
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class ProfileType(str, Enum):
    PERSONAL = "Personal"
    COMPANY = "Company"
    PRODUCT = "Product"
    OTHER = "Other"

class PlatformPriority(str, Enum):
    LINKEDIN_PRIMARY = "LinkedIn primary"
    TWITTER_PRIMARY = "Twitter primary"
    BOTH_EQUAL = "Both equal"

class BrandProfile(BaseModel):
    profile_id: str
    profile_name: str
    profile_type: ProfileType

    # Social handles
    linkedin_username: Optional[str] = None
    twitter_username: Optional[str] = None

    # Content strategy
    target_audience: str
    tone: str
    key_topics: List[str]
    platform_priority: PlatformPriority

    # Brand identity
    bio: str
    avatar_url: Optional[str] = None

    # Active status
    is_active: bool = True
```

---

## First-Time Setup Flow

### Step 1: Welcome Screen
```
Welcome to LinkedIn Content Pipeline!

Let's set up your account in 3 minutes.

[Get Started] button
```

### Step 2: Basic Profile
```
Tell us about yourself:
- Full Name: [________]
- Email: [________]
- Timezone: [Dropdown]

[Next]
```

### Step 3: Social Accounts
```
Connect your social media accounts:

LinkedIn:
- Username or Profile URL: [________]
- [ ] I'll add this later

Twitter/X:
- Handle (with @): [________]
- [ ] I'll add this later

[Next]
```

### Step 4: First Brand Profile
```
Create your first brand profile:

What type of content will you create?
( ) Personal Brand - Build my professional presence
( ) Company Brand - Promote my company
( ) Product Brand - Market my product
( ) I'll set this up later

Profile Name: [________]
Target Audience: [________]
Content Tone: [Dropdown: Professional / Friendly / Authoritative / etc.]

[Create Profile]
```

### Step 5: Google Sheets Setup
```
Connect to Google Sheets:

1. We'll create a Google Sheet template for you
2. Click [Authorize Google Sheets] to connect
3. Copy the sheet ID back here

Sheet ID: [________]
[Test Connection]

[Or] Use this template: [Copy Template Link]

[Next]
```

### Step 6: AI Model Setup
```
Choose your AI model:

( ) Ollama (Local, Free)
    - Download Ollama: [Link]
    - Run: ollama pull llama3.1:8b
    - [Test Connection]

( ) Google Gemini (Cloud, Free Tier)
    - API Key: [________]
    - [Test Connection]

( ) I'll set this up later (Demo mode)

[Finish Setup]
```

---

## Settings Persistence

### On App Start
1. Check if `.env` exists
2. Check if Google Sheets is connected
3. Load settings from "Settings" tab
4. Load brand profiles from "Brand_Profiles" tab
5. If missing, show first-time setup wizard

### On Settings Change
1. Validate new settings (Pydantic models)
2. Save to Google Sheets immediately
3. Show confirmation toast
4. Refresh cached settings

### Settings Cache
- Settings loaded once at startup
- Cached in Streamlit session state
- "Refresh Settings" button to reload
- Auto-refresh after edits

---

## Multi-User Support

### Option A: Single Google Sheet per User (Recommended)
- Each user has their own Google Sheet
- Sheet ID stored in local `.env`
- Complete isolation
- Easy backup/sharing

### Option B: Multi-Tenant Google Sheet
- Single sheet with "User_ID" column
- User selects profile on login
- More complex but single source of truth

**Recommendation:** Use Option A (one sheet per user) for simplicity.

---

## Configuration Export/Import

### Export Settings
```
Settings -> Export Configuration
- Creates JSON file with all settings
- Excludes sensitive credentials (API keys)
- Includes brand profiles, preferences
- Can share with team or backup
```

### Import Settings
```
Settings -> Import Configuration
- Upload JSON file
- Preview changes
- Confirm import
- Merges with existing settings
```

### Team Templates
```
Settings -> Load Template
- Pre-configured templates for common use cases:
  - Tech Founder Template
  - B2B SaaS Company Template
  - Product Marketing Template
  - Consultant/Coach Template
```

---

## Security Considerations

### Sensitive Data (.env)
- Never committed to version control
- `.gitignore` includes `.env`
- Encrypted at rest (user's responsibility)
- Not stored in Google Sheets

### Google Sheets Data
- Non-sensitive preferences only
- Share settings with read-only permissions
- Use service account for app access
- User OAuth for personal access

### Credentials UI
- API keys shown as `****` (masked)
- "Show/Hide" toggle
- "Test Connection" before saving
- Clear error messages if invalid

---

## Configuration File Structure

### `.env` (Local, Sensitive)
```env
# Google Sheets
GOOGLE_SHEETS_CREDS_FILE=./credentials.json
GOOGLE_SHEET_ID=your-sheet-id-here

# AI Service
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Optional: Gemini API
GOOGLE_GEMINI_API_KEY=your-api-key

# Twitter API (if auto-posting)
TWITTER_API_KEY=your-key
TWITTER_API_SECRET=your-secret
TWITTER_ACCESS_TOKEN=your-token
TWITTER_ACCESS_TOKEN_SECRET=your-token-secret

# LinkedIn API (if using)
LINKEDIN_EMAIL=your-email
LINKEDIN_PASSWORD=your-password

# App Settings
DEBUG_MODE=False
LOG_LEVEL=INFO
```

### `config.json` (Optional, Non-Sensitive Backup)
```json
{
  "version": "1.0.0",
  "last_updated": "2025-01-18T10:30:00Z",
  "settings": {
    "user_full_name": "John Doe",
    "default_timezone": "America/New_York",
    "content_tone_default": "Professional & Friendly"
  },
  "brand_profiles": [
    {
      "profile_id": "personal_001",
      "profile_name": "Personal Brand",
      "target_audience": "Tech founders and leaders"
    }
  ]
}
```

---

## Implementation Checklist

- [ ] Create "Settings" tab in Google Sheet template
- [ ] Create "Brand_Profiles" tab in Google Sheet template
- [ ] Build Streamlit settings page with all tabs
- [ ] Implement Pydantic models for validation
- [ ] Create first-time setup wizard
- [ ] Add settings cache to session state
- [ ] Build export/import functionality
- [ ] Create default templates
- [ ] Add "Test Connection" buttons for all APIs
- [ ] Implement settings sync (Google Sheets ↔ App)
- [ ] Add configuration validation on startup
- [ ] Create user documentation for settings

---

## Example: Switching Between Profiles

### UI Flow
```
Content Generation Page:

Brand Profile: [Dropdown]
  - Personal Brand (personal_001)
  - Company Brand (company_001)
  - Product Brand (product_001)
  - [+ Add New Profile]

[When selected, auto-loads:]
- LinkedIn username: john_doe
- Twitter username: @johndoe
- Tone: Authentic & Insightful
- Target audience: Tech professionals
```

### Backend
```python
# Load selected profile
profile = load_brand_profile(profile_id="personal_001")

# Override defaults for this generation
generation_config = {
    "tone": profile.tone,
    "target_audience": profile.target_audience,
    "linkedin_username": profile.linkedin_username,
    "twitter_username": profile.twitter_username,
    "platform_priority": profile.platform_priority
}

# Run pipeline with profile settings
result = run_pipeline(
    ideas=selected_ideas,
    config=generation_config
)
```

---

Ready to proceed with implementation?
