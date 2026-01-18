# Technical Requirements & Dependencies

## System Requirements

### Minimum Hardware
- **RAM:** 8GB (16GB recommended for better AI performance)
- **Storage:** 10GB free space for AI models
- **CPU:** Multi-core processor (4+ cores recommended)
- **GPU:** Optional but recommended (NVIDIA with 6GB+ VRAM for faster AI)

### Software Requirements
- **Python:** 3.9 or higher
- **Operating System:** Windows, macOS, or Linux
- **Internet:** Required for Google Sheets API and (optionally) API-based AI

---

## Python Dependencies

### Core Framework
```
streamlit>=1.28.0           # Web UI framework
```

### Google Sheets Integration
```
gspread>=5.12.0             # Google Sheets API wrapper
google-auth>=2.23.0         # Authentication
google-auth-oauthlib>=1.1.0 # OAuth flow
google-auth-httplib2>=0.1.1 # HTTP library
```

### AI/LLM Integration
```
ollama>=0.1.0               # Ollama Python client (local AI)
langchain>=0.1.0            # Optional: LLM orchestration
```

### Social Media APIs
```
linkedin-api>=2.0.0         # Unofficial LinkedIn API
tweepy>=4.14.0              # Twitter/X API client
```

### Data & Utilities
```
pandas>=2.0.0               # Data manipulation
python-dotenv>=1.0.0        # Environment variables
pydantic>=2.0.0             # Data validation
```

### Optional - Better AI Quality
```
google-generativeai>=0.3.0  # Google Gemini API (free tier option)
```

---

## Ollama Setup

### Installation

**Windows:**
```bash
# Download from https://ollama.ai/download
# Run installer
```

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Recommended Models

**For Content Generation:**
```bash
# Best quality (requires 8GB RAM)
ollama pull llama3.1:8b

# Lighter option (requires 4GB RAM)
ollama pull mistral:7b

# Fastest option (requires 2GB RAM)
ollama pull phi3:mini
```

**Model Selection Guide:**
- **llama3.1:8b** - Best overall quality, good for content writing
- **mistral:7b** - Good balance of speed and quality
- **phi3:mini** - Fastest, lower quality but acceptable

---

## Google Cloud Setup

### Enable Google Sheets API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: "LinkedIn Content Pipeline"
3. Enable APIs:
   - Google Sheets API
   - Google Drive API
4. Create credentials:
   - OAuth 2.0 Client ID (for user access)
   - Service Account (for app access)
5. Download credentials JSON file

### Create Google Sheet Template

Create a new Google Sheet with three tabs:

**Tab 1: "Content_Ideas"**
- Column headers: `ID | Timestamp | Idea_Text | Category | Source | Used | Used_Date`

**Tab 2: "Generated_Content"**
- Column headers: `ID | Generation_Date | Source_Ideas | Audience_Type | LinkedIn_Post | Twitter_Thread | Status | Published_Date | Performance`

**Tab 3: "Audience_Profiles"**
- Column headers: `Profile_Name | Target_Audience | Tone | Key_Topics | Platform_Preferences`

Share the sheet with your service account email (found in credentials JSON).

---

## Social Media API Setup

### LinkedIn API (Unofficial)
⚠️ **Note:** LinkedIn doesn't offer free posting API. Options:
1. Use unofficial `linkedin-api` (scraping-based, risk of account issues)
2. Manual posting (safest for now)
3. Wait for official API access (requires company page)

**Recommendation:** Start with manual posting, add automation later.

### Twitter/X API
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Sign up for API access
3. Select plan:
   - **Free Tier:** Read-only (can't post)
   - **Basic ($100/month):** Can post tweets
4. Get API credentials:
   - API Key
   - API Secret
   - Access Token
   - Access Token Secret

**Recommendation:** Start with manual posting to avoid $100/month cost.

---

## Environment Variables

Create `.env` file in project root:

```env
# Google Sheets
GOOGLE_SHEETS_CREDS_FILE=path/to/credentials.json
GOOGLE_SHEET_ID=your-sheet-id-here

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Optional: Gemini API (fallback for better quality)
GOOGLE_GEMINI_API_KEY=your-api-key-here

# Twitter/X API (if using)
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-access-token-secret

# LinkedIn (if using unofficial API)
LINKEDIN_EMAIL=your-email
LINKEDIN_PASSWORD=your-password
```

---

## Project Structure

```
linkedin-content-pipeline/
├── .env                          # Environment variables (DO NOT COMMIT)
├── .gitignore                    # Ignore .env, credentials, etc.
├── requirements.txt              # Python dependencies
├── README.md                     # User documentation
├── ARCHITECTURE.md               # This document
├── TECHNICAL_REQUIREMENTS.md     # Technical setup guide
│
├── app.py                        # Main Streamlit app entry point
│
├── config/
│   ├── __init__.py
│   ├── settings.py               # Load env vars, config
│   └── google_sheets_setup.py    # Google Sheets connection
│
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── google_sheets.py      # Google Sheets CRUD operations
│   │   └── models.py             # Pydantic data models
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── stage1_curation.py    # Topic curation logic
│   │   ├── stage2_development.py # Content development logic
│   │   ├── stage3_optimization.py # Platform optimization logic
│   │   └── orchestrator.py       # Run full pipeline
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── ollama_client.py      # Ollama integration
│   │   └── prompts.py            # AI prompt templates
│   │
│   ├── platforms/
│   │   ├── __init__.py
│   │   ├── linkedin.py           # LinkedIn posting (manual/API)
│   │   └── twitter.py            # Twitter/X posting (manual/API)
│   │
│   └── ui/
│       ├── __init__.py
│       ├── idea_entry.py         # UI for entering ideas
│       ├── content_review.py     # UI for reviewing content
│       └── analytics.py          # UI for viewing metrics
│
├── prompts/
│   ├── stage1_topic_curation.txt
│   ├── stage2_content_development.txt
│   └── stage3_optimization.txt
│
└── tests/
    ├── __init__.py
    ├── test_google_sheets.py
    ├── test_pipeline.py
    └── test_ai.py
```

---

## Installation Steps

### 1. Install Python Dependencies
```bash
cd linkedin-content-pipeline
pip install -r requirements.txt
```

### 2. Install Ollama
Follow OS-specific instructions above, then:
```bash
ollama serve  # Start Ollama service
ollama pull llama3.1:8b  # Download model
```

### 3. Set Up Google Sheets
1. Create Google Cloud project
2. Enable APIs
3. Download credentials JSON
4. Create Google Sheet from template
5. Add credentials path to `.env`

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your values
```

### 5. Run Application
```bash
streamlit run app.py
```

---

## Testing Checklist

- [ ] Ollama service running and responding
- [ ] Google Sheets connection successful
- [ ] Can read/write to Google Sheets
- [ ] AI model generates coherent text
- [ ] Streamlit UI loads without errors
- [ ] Idea entry form works
- [ ] Pipeline runs end-to-end
- [ ] Content output is formatted correctly

---

## Troubleshooting

### Ollama Not Responding
```bash
# Check if service is running
ollama list

# Restart service
ollama serve
```

### Google Sheets Permission Denied
- Verify service account email has access to sheet
- Check credentials JSON file path in `.env`
- Ensure Google Sheets API is enabled

### Out of Memory Errors
- Switch to smaller model: `ollama pull phi3:mini`
- Close other applications
- Increase system swap space

### Slow AI Generation
- Use GPU if available
- Switch to faster model
- Consider using Google Gemini API instead

---

Ready to start building?
