# LinkedIn Content Pipeline - Architecture Design

## Executive Summary

A flexible, multi-platform content generation system with web UI for entering ideas, storing them in Google Sheets, and using local AI models to generate optimized content for LinkedIn and Twitter/X.

---

## Key Differences from Original

| Feature | Original | Your Version |
|---------|----------|--------------|
| Content Source | Notion journal | Web UI + Google Sheets |
| AI Service | Not specified | Local/Open source (Ollama) |
| Audience | Fixed transition path | Dynamic UI selection per run |
| Platforms | LinkedIn only | LinkedIn + Twitter/X |
| Cost | Requires paid APIs | Free/minimal cost |
| User Base | Single user | Designed for anyone to use |

---

## Recommended Tech Stack

**Backend & UI: Streamlit (Python)**
- ✅ Rapid development, all-Python stack
- ✅ Built-in UI components (forms, buttons, data tables)
- ✅ Easy to deploy (Streamlit Community Cloud free tier)
- ✅ Great for AI/data apps
- ✅ No frontend framework needed

**Data Storage: Google Sheets API**
- ✅ Free (your choice)
- ✅ Easy manual editing/viewing
- ✅ Familiar interface for non-technical users
- ✅ Built-in version history
- ✅ Easy sharing and collaboration

**AI: Ollama (Local LLMs)**
- ✅ Completely free
- ✅ Privacy-focused (data stays local)
- ✅ Multiple model options (Llama 3.1, Mistral, etc.)
- ⚠️ Requires ~8GB RAM, decent CPU/GPU
- ⚠️ Quality lower than Claude/GPT-4 but sufficient

**Fallback Option:** Provide easy config to swap in Google Gemini API (free tier) for better quality

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Web UI                        │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ Idea Entry   │  │ Audience     │  │ Content Review  │  │
│  │ Form         │  │ Selector     │  │ & Scheduling    │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└────────────┬────────────────────────────────────┬──────────┘
             │                                     │
             ▼                                     ▼
    ┌────────────────┐                   ┌─────────────────┐
    │ Google Sheets  │                   │ Content Output  │
    │ API Layer      │                   │ Manager         │
    └────────┬───────┘                   └────────┬────────┘
             │                                     │
             ▼                                     ▼
    ┌────────────────┐                   ┌─────────────────┐
    │ Ideas Sheet    │                   │ Platform APIs   │
    │ (Storage)      │                   │ (LinkedIn, X)   │
    └────────────────┘                   └─────────────────┘
             │
             ▼
    ┌────────────────────────────────────────────────────────┐
    │           Content Generation Pipeline                   │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
    │  │ Stage 1:     │→ │ Stage 2:     │→ │ Stage 3:     │ │
    │  │ Topic        │  │ Content      │  │ Platform     │ │
    │  │ Curation     │  │ Development  │  │ Optimization │ │
    │  └──────────────┘  └──────────────┘  └──────────────┘ │
    │                   (Ollama LLM)                          │
    └────────────────────────────────────────────────────────┘
```

---

## Google Sheets Structure

### Sheet 1: "Content Ideas"
| Column | Description | Example |
|--------|-------------|---------|
| ID | Auto-generated | `idea-001` |
| Timestamp | When entered | `2025-01-18 09:30:00` |
| Idea Text | Raw idea/observation | "Noticed our team struggles with async updates..." |
| Category | User-selected tag | "Team Management", "AI Tools", "Personal Growth" |
| Source | Where it came from | "Web UI", "Mobile Note", "Email" |
| Used | Boolean flag | `FALSE` |
| Used Date | When converted to content | `2025-01-20` |

### Sheet 2: "Generated Content"
| Column | Description |
|--------|-------------|
| ID | Content batch ID |
| Generation Date | When pipeline ran |
| Source Ideas | Which idea IDs used |
| Audience Type | Which persona selected |
| LinkedIn Post | Optimized LinkedIn version |
| Twitter Thread | Optimized Twitter/X version |
| Status | Draft/Scheduled/Published |
| Published Date | When posted |
| Performance | Engagement metrics |

### Sheet 3: "Audience Profiles"
| Column | Description |
|--------|-------------|
| Profile Name | "Personal Brand", "Company Brand", etc. |
| Target Audience | Description of who |
| Tone | Voice/style guidelines |
| Key Topics | Focus areas |
| Platform Preferences | Which platforms to prioritize |

---

## Key Features

### 1. Web UI for Idea Entry
- Simple form: text area + category dropdown
- "Quick capture" mode for rapid entries
- View all stored ideas in table
- Edit/delete existing ideas
- Filter by category, date, used/unused

### 2. Dynamic Audience Selection
- Dropdown to select audience profile at runtime
- Pre-configured profiles stored in Google Sheet
- Each profile defines:
  - Target audience description
  - Tone/voice
  - Content style preferences
  - Platform priorities

### 3. Content Generation Pipeline
Same three stages as original, but adapted:
- **Stage 1:** Query Google Sheets for unused ideas, analyze patterns
- **Stage 2:** Generate 3 content versions (Bridge, Aspirational, Current)
- **Stage 3:** Optimize for LinkedIn AND Twitter/X

### 4. Multi-Platform Support
- LinkedIn: 1,300-2,000 chars, story hooks, professional formatting
- Twitter/X: Thread format (280 chars per tweet), punchy hooks, engagement tactics
- Future: Easy to add Medium, Instagram, etc.

### 5. Content Review & Scheduling
- Review generated content before posting
- Edit if needed
- Schedule posts or save as drafts
- Track what's been published

### 6. Analytics & Tracking
- Track which ideas generate content
- Store engagement metrics (likes, comments, shares)
- Identify top-performing content types
- A/B test different versions

---

## Cost Analysis

| Component | Cost | Notes |
|-----------|------|-------|
| Streamlit Hosting | FREE | Community Cloud (public repos) |
| Google Sheets API | FREE | Up to 10M cells |
| Ollama (Local AI) | FREE | Requires local compute |
| LinkedIn API | FREE | Personal use, rate limits apply |
| Twitter API | $100/month | Basic tier for posting (⚠️ expensive) |
| **Total Monthly** | **$0-100** | $0 if manual posting, $100 if auto-tweet |

**Recommendation:** Start with manual posting for Twitter to keep it free, add API later if needed.

---

## Next Steps

1. Set up project structure
2. Configure Google Sheets template
3. Install Ollama and test models
4. Build Streamlit UI prototype
5. Implement Stage 1 (Topic Curation)
6. Implement Stage 2 (Content Development)
7. Implement Stage 3 (Platform Optimization)
8. Add scheduling and publishing features
9. Implement analytics tracking

Ready to proceed with setup?
