# Setup Guide

Complete setup instructions for the LinkedIn Content Pipeline.

## Quick Start (Demo Mode)

Get started in 2 minutes with demo mode (no API keys required):

```bash
# 1. Clone repository
git clone https://github.com/blakehow/linkedin-content-pipeline.git
cd linkedin-content-pipeline

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file (copy from example)
cp .env.example .env

# 5. Load sample data
python load_sample_data.py

# 6. Run the app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Full Setup (Production)

### Prerequisites

- Python 3.9 or higher
- 8GB RAM minimum (for local AI models)
- Git

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Choose Your AI Service

#### Option A: Ollama (Local, Free, Private)

**Pros:** Free, private, no API key needed
**Cons:** Requires local compute, slower than cloud APIs

1. Install Ollama from [ollama.ai](https://ollama.ai/download)

2. Pull a model:
```bash
# Recommended (best quality)
ollama pull llama3.1:8b

# Or lighter option
ollama pull mistral:7b

# Or fastest option
ollama pull phi3:mini
```

3. Start Ollama service:
```bash
ollama serve
```

4. Update `.env`:
```env
AI_SERVICE_PRIMARY=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

#### Option B: Google Gemini (Cloud, Free Tier)

**Pros:** Fast, good quality, free tier available
**Cons:** Requires API key, sends data to Google

1. Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

2. Update `.env`:
```env
AI_SERVICE_PRIMARY=gemini
GOOGLE_GEMINI_API_KEY=your-api-key-here
```

#### Option C: Hybrid (Best of Both)

Use Ollama as primary with Gemini as fallback:

```env
AI_SERVICE_PRIMARY=ollama
AI_SERVICE_FALLBACK=gemini
GOOGLE_GEMINI_API_KEY=your-api-key-here
```

### 3. Data Storage

#### Default: Local JSON Files

Works out of the box - no setup needed. Data stored in `./data/` directory.

#### Optional: Google Sheets

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project
3. Enable Google Sheets API and Google Drive API
4. Create service account credentials
5. Download credentials JSON
6. Update `.env`:
```env
DATA_STORAGE_TYPE=google_sheets
GOOGLE_SHEETS_CREDS_FILE=./credentials.json
GOOGLE_SHEET_ID=your-sheet-id-here
```

### 4. Configure Settings

Edit `.env` file:

```env
# Application
APP_ENV=production
DEBUG_MODE=False
DEMO_MODE=False

# Data Storage
DATA_STORAGE_TYPE=mock  # or google_sheets

# AI Service (choose one)
AI_SERVICE_PRIMARY=ollama  # or gemini or mock
AI_SERVICE_FALLBACK=gemini  # optional

# Ollama (if using)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Google Gemini (if using)
GOOGLE_GEMINI_API_KEY=your-api-key

# Demo Mode (for testing)
DEMO_MODE=False
LOAD_SAMPLE_DATA=False
```

### 5. Load Sample Data (Optional)

```bash
python load_sample_data.py
```

This creates:
- Sample user profile
- 2 brand profiles
- 12 example content ideas

### 6. Run the Application

```bash
streamlit run app.py
```

## Platform Integration (Optional)

### LinkedIn API

⚠️ **Note:** LinkedIn doesn't provide free posting API for personal accounts.

**Options:**
1. Manual posting (recommended)
2. Use unofficial `linkedin-api` library (risk of account issues)
3. Apply for LinkedIn Developer Program (company page required)

### Twitter/X API

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Sign up for API access
3. Choose plan:
   - Free: Read-only
   - Basic ($100/month): Can post tweets

4. Get credentials and update `.env`:
```env
TWITTER_API_KEY=your-key
TWITTER_API_SECRET=your-secret
TWITTER_ACCESS_TOKEN=your-token
TWITTER_ACCESS_TOKEN_SECRET=your-token-secret
```

**Recommendation:** Start with manual posting to avoid $100/month cost.

## Troubleshooting

### Ollama Not Starting

```bash
# Check if running
ollama list

# Restart service
ollama serve

# Check logs
ollama logs
```

### Out of Memory

- Switch to smaller model: `ollama pull phi3:mini`
- Close other applications
- Increase system swap space
- Use Gemini API instead

### Slow Generation

- Use GPU if available
- Switch to faster model (phi3:mini)
- Use Gemini API for better speed

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Port Already in Use

```bash
# Use different port
streamlit run app.py --server.port 8502
```

## Security Checklist

Before deploying:

- [ ] `.env` file in `.gitignore`
- [ ] API keys never committed
- [ ] `DEBUG_MODE=False` in production
- [ ] Strong passwords if deploying publicly
- [ ] HTTPS enabled for public deployment
- [ ] Regular dependency updates

## Deployment

### Streamlit Community Cloud (Free)

1. Push code to GitHub (ensure `.env` not committed)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Add secrets in Streamlit dashboard (same as `.env`)
5. Deploy!

### Docker

```bash
# Build image
docker build -t linkedin-content-pipeline .

# Run container
docker run -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -e AI_SERVICE_PRIMARY=gemini \
  -e GOOGLE_GEMINI_API_KEY=your-key \
  linkedin-content-pipeline
```

## Next Steps

1. Configure your user profile in Settings
2. Create your first brand profile
3. Add 5-10 content ideas
4. Run the pipeline!

## Support

- Documentation: [README.md](README.md)
- Issues: [GitHub Issues](https://github.com/blakehow/linkedin-content-pipeline/issues)
- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
