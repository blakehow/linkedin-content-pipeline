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

## Quick Start

### Prerequisites

- Python 3.9+
- 8GB RAM (for local AI models)
- Google account
- Ollama installed

### Installation

```bash
# Clone repository
git clone https://github.com/blakehow/linkedin-content-pipeline.git
cd linkedin-content-pipeline

# Install dependencies
pip install -r requirements.txt

# Install Ollama
# Visit: https://ollama.ai/download

# Pull AI model
ollama pull llama3.1:8b

# Run app
streamlit run app.py
```

### First-Time Setup

The app will guide you through:
1. Connecting Google Sheets
2. Setting up your profile
3. Adding social media accounts
4. Creating your first brand profile

## Documentation

- [Architecture](ARCHITECTURE.md) - System design and tech stack
- [Technical Requirements](TECHNICAL_REQUIREMENTS.md) - Setup instructions
- [User Configuration](USER_CONFIGURATION.md) - Settings and profiles
- [Testing Plan](TESTING_PLAN.md) - Quality assurance strategy
- [Security Audit](SECURITY_AUDIT.md) - Security checklist

## Project Status

🚧 **In Development** - Design phase complete, implementation in progress

## Contributing

Contributions welcome! Please see our contributing guidelines (coming soon).

## License

MIT License (coming soon)

## Contact

For questions or support, please open an issue on GitHub.
