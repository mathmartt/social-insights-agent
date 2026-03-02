# Social Insights Agent

An internal marketing intelligence tool for Google's marketing org. A PMM or marketing manager types a natural language question and gets back a trusted, evidence-backed answer — replacing the need to commission an agency for social listening reports.

> **"What are users saying about Android camera quality across our Q4 campaigns?"**

The agent reads your owned social data, applies Gemini's reasoning to find what's truly relevant, and returns a structured report with sentiment analysis, key themes, specific action items, and verbatim comment evidence.

---

## Screenshots

| Search | Results |
|--------|---------|
| Clean, confident search bar with suggested queries | Sentiment breakdown, trend charts, action items, and comment evidence cards |

---

## Features

- **Natural language queries** — ask anything about your social data in plain English, Portuguese, or Spanish
- **Gemini thinking mode** — `gemini-3.1-pro-preview` with extended reasoning; the full chain of thought is surfaced in the Reasoning Panel
- **Multilingual** — English, Portuguese, and Spanish comments handled equally
- **Precision over recall** — semantic understanding, not keyword matching; irrelevant/spam comments are excluded and explained
- **Sentiment analysis** — % Positive / Neutral / Negative with trend over time and breakdown by platform (Recharts)
- **Key themes** — auto-extracted topic clusters from relevant comments
- **Action items** — 2–4 specific, grounded recommendations that feel like they came from a senior analyst
- **Comment evidence** — card grid of verbatim comments, color-coded by sentiment, with platform icon, date, and likes
- **Reasoning panel** — collapsible plain-English explanation of what the agent looked for and why comments were included or excluded
- **Follow-up chat** — persistent conversational thread that maintains full context of the current results
- **Export to PowerPoint** — presentation-ready 5-slide `.pptx` deck with Google branding
- **Export to CSV** — all relevant comments with full metadata
- **Data status panel** — gear icon shows live data info (total rows, date range, platforms, campaigns)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite |
| Charts | Recharts |
| Icons | react-icons |
| Styling | Custom CSS with Google design tokens |
| Backend | Python 3.9+ / FastAPI |
| AI | Google Gemini (`gemini-3.1-pro-preview`) via `google-genai` SDK |
| Data | CSV loaded into memory at startup via pandas |
| Export | python-pptx (PowerPoint), pandas (CSV) |

---

## Project Structure

```
social-insights-agent/
├── backend/
│   ├── main.py                        # FastAPI app — all API endpoints
│   ├── generate_mock_data.py          # One-time script to generate mock CSV
│   ├── requirements.txt
│   ├── data/
│   │   └── mock_data.csv              # 620-row multilingual dataset
│   └── services/
│       ├── gemini_service.py          # Gemini API integration + prompts
│       ├── data_service.py            # CSV loading + keyword pre-filtering
│       └── export_service.py          # PowerPoint + CSV export
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js                 # Dev server proxy → backend:8000
    └── src/
        ├── App.jsx                    # Root — view routing, state
        ├── api.js                     # All fetch calls to backend
        ├── index.css                  # Google design system (CSS variables)
        └── components/
            ├── SearchPage.jsx         # Hero search + suggestion chips
            ├── LoadingState.jsx       # Animated 5-step progress indicator
            ├── ResultsPage.jsx        # Results layout assembly
            ├── InsightHeader.jsx      # Query + stats badges
            ├── SentimentSummary.jsx   # Big 3 numbers + AreaChart + BarChart
            ├── WrittenSummary.jsx     # Synthesis paragraph + theme pills
            ├── ActionItems.jsx        # Priority-coded recommendation cards
            ├── CommentEvidence.jsx    # Comment card grid + expandable table
            ├── ReasoningPanel.jsx     # Collapsible chain-of-thought
            ├── FollowUpChat.jsx       # Persistent conversation thread
            └── SettingsModal.jsx      # Read-only data status panel
```

---

## Setup & Running

### Prerequisites

- Python 3.9+
- Node.js 18+ (via nvm or direct install)
- A [Google AI Studio](https://aistudio.google.com) API key

### 1. Install backend dependencies

```bash
cd backend
pip3 install -r requirements.txt
```

### 2. Generate mock data (first time only)

```bash
cd backend
python3 generate_mock_data.py
# ✅ Generated 620 rows → data/mock_data.csv
```

This creates a realistic 620-row dataset with comments in English, Portuguese, and Spanish covering camera quality, battery life, AI features, security, iOS comparisons, pricing, and regional concerns — plus ~20% realistic noise (spam, emojis, off-topic rants) to demonstrate the agent's filtering.

To use your own data instead, place a CSV at `backend/data/mock_data.csv` with these columns:

| Column | Description |
|--------|-------------|
| `date` | Post date (YYYY-MM-DD) |
| `google_account` | e.g. `googlebrasil`, `Android` |
| `social_network` | Instagram / TikTok / YouTube / Facebook / X / Threads / Reddit |
| `post_caption` | Caption text of the original post |
| `asset_url` | Media URL |
| `campaign_name` | e.g. `Pixel Camera Q4` |
| `comment_text` | The user comment |
| `comment_sentiment` | `Positive` / `Neutral` / `Negative` |
| `comment_likes` | Integer |
| `comment_author` | Username string |
| `comment_date` | Datetime (YYYY-MM-DD HH:MM:SS) |

### 3. Start the backend

```bash
cd backend
GEMINI_API_KEY=your_key_here python3 -m uvicorn main:app --reload --port 8000
```

You should see:
```
✅  Gemini API key loaded.
✅  Loaded 620 rows from .../data/mock_data.csv
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 4. Start the frontend

```bash
cd frontend
npm install      # first time only
npm run dev
```

### 5. Open the app

Navigate to [http://localhost:5173](http://localhost:5173)

---

## API Reference

All endpoints served at `http://localhost:8000`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check + data/key status |
| `GET` | `/api/data-info` | Dataset metadata (rows, date range, platforms) |
| `POST` | `/api/query` | Run a main analysis query |
| `POST` | `/api/follow-up` | Ask a follow-up in context of current results |
| `POST` | `/api/export/pptx` | Generate and download PowerPoint report |
| `POST` | `/api/export/csv` | Download relevant comments as CSV |

### POST /api/query

```json
{
  "query": "What are users saying about Pixel camera quality in Brazil?"
}
```

### POST /api/follow-up

```json
{
  "query": "How does this compare to last quarter?",
  "conversation_history": [...],
  "current_results": {...}
}
```

---

## How the Agent Works

### Query pipeline

```
User query
    ↓
Keyword pre-filter (data_service.py)
    → Extracts meaningful keywords, filters CSV to ~250 candidate comments
    ↓
Gemini analysis (gemini_service.py)
    → Extended thinking mode (10,000 token budget)
    → Semantic relevance filtering (not keyword matching)
    → Multilingual understanding (EN / PT / ES)
    → Structured JSON response
    ↓
Result hydration
    → Relevant comment IDs → full comment objects
    → Thinking chain captured and surfaced
    ↓
Frontend renders results
```

### Agent rules (enforced in system prompt)

1. **Precision over recall** — a comment mentioning "Android" is not automatically about camera quality
2. **Multilingual** — Portuguese and Spanish comments are never downweighted
3. **Transparency** — every inclusion/exclusion decision is explained in the Reasoning Panel
4. **Honesty** — if data is thin, the agent says so clearly rather than faking confidence
5. **Specificity** — action items are grounded in actual comment patterns, never generic

### PowerPoint export (5 slides)

| Slide | Content |
|-------|---------|
| 1 | Title — query, date range, comments analysed |
| 2 | Sentiment overview — three big numbers + trend data |
| 3 | Key findings — written summary + themes |
| 4 | Action items — priority-coded recommendations |
| 5 | Comment evidence — positive / neutral / negative columns |

Footer on all slides: *"Source: Google Owned Social Handles via Sprinklr"*

---

## Development Notes

- The Vite dev server proxies `/api/*` to `localhost:8000`, so no CORS issues in development
- The backend reads `GEMINI_API_KEY` from the environment at startup — never from the client
- Gemini thinking parts are identified via `part.thought == True` in the response; the thinking chain is stored separately and shown in the collapsible Reasoning Panel
- The pre-filter in `data_service.py` extracts keywords from the query (minus stop words) and searches `comment_text`, `post_caption`, and `campaign_name`. If fewer than 30 matches are found, it falls back to a random sample to ensure Claude always has enough context
- Mock data uses `random.seed(42)` for reproducibility

---

## Folder-level `.gitignore` summary

| Ignored | Reason |
|---------|--------|
| `frontend/node_modules/` | npm packages — install locally |
| `frontend/dist/` | Build output |
| `__pycache__/`, `*.pyc` | Python bytecode |
| `.env`, `.env.*` | Secrets |
| `.DS_Store` | macOS metadata |
