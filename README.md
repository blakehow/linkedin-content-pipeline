# LinkedIn Content Pipeline

A flexible, multi-platform content generation system with web UI for creating and optimizing social media content using local AI models.

## Features

- **Web UI** for easy idea entry and content management
- **Google Sheets** integration for data storage
- **Local AI** powered by Ollama (free, privacy-focused)
- **Multi-platform** support (LinkedIn + Twitter/X)
- **Multiple brand profiles** (Personal, Company, Product)
- **Three-stage pipeline**: Topic Curation → Content Development → Platform Optimization
- **Scheduling & analytics** for tracking performance

## Cost

**$0-100/month** depending on features used:
- Core app: FREE
- Google Sheets: FREE
- Ollama AI: FREE
- Twitter API (optional): $100/month

## Quick Start (2 Minutes)

Demo mode requires no API keys or setup:

```bash
# 1. Clone and install
git clone https://github.com/blakehow/linkedin-content-pipeline.git
cd linkedin-content-pipeline
pip install -r requirements.txt

# 2. Create .env file
cp .env.example .env

# 3. Load sample data
python load_sample_data.py

# 4. Run app
streamlit run app.py
```

The app opens at `http://localhost:8501` with sample data ready to explore.

## Full Setup

For production use with real AI:

**Option A: Ollama (Local, Free)**
```bash
# Install Ollama from ollama.ai
ollama pull llama3.1:8b
ollama serve

# Update .env
AI_SERVICE_PRIMARY=ollama
```

**Option B: Google Gemini (Cloud, Free Tier)**
```bash
# Get API key from makersuite.google.com
# Update .env
AI_SERVICE_PRIMARY=gemini
GOOGLE_GEMINI_API_KEY=your-key
```

See [SETUP.md](SETUP.md) for detailed instructions.

## Documentation

- [Architecture](ARCHITECTURE.md) - System design and tech stack
- [Technical Requirements](TECHNICAL_REQUIREMENTS.md) - Setup instructions
- [User Configuration](USER_CONFIGURATION.md) - Settings and profiles
- [Testing Plan](TESTING_PLAN.md) - Quality assurance strategy
- [Security Audit](SECURITY_AUDIT.md) - Security checklist

## Project Status

✅ **Fully Functional** - All core features implemented and ready to use

**Completed:**
- ✅ Complete 3-stage content pipeline
- ✅ Streamlit web UI with 6 pages
- ✅ Mock AI + Ollama + Gemini support with fallback
- ✅ Configurable prompt templates
- ✅ Mock storage (JSON files)
- ✅ Demo mode with sample data
- ✅ User settings and brand profiles

**Roadmap:**
- 🔄 Google Sheets integration
- 🔄 LinkedIn/Twitter API integration for auto-posting
- 🔄 Analytics and performance tracking
- 🔄 Test suite
- 🔄 Docker deployment

## Contributing

Contributions welcome! Please see our contributing guidelines (coming soon).

## License

MIT License (coming soon)

## Contact

For questions or support, please open an issue on GitHub.
