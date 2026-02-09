# LLM Lab

A production-ready full-stack application for experimenting with LLM parameters, generating multiple responses, and analyzing response quality through custom metrics.

## Architecture

- **Backend**: FastAPI + LangChain + OpenAI + SQLite/PostgreSQL
- **Frontend**: Next.js 14+ (App Router) + TanStack Query + Modern UI components

## Features

- Interactive prompt editor
- Parameter range controls (temperature, top_p, max_tokens, presence_penalty, frequency_penalty)
- Batch LLM response generation
- Side-by-side response comparison
- Custom quality metrics (coherence, completeness, length appropriateness, repetition penalty, structural richness)
- Experiment persistence and history
- Export to JSON/CSV

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── models/              # Pydantic models
│   ├── services/            # Business logic
│   │   ├── llm_service.py   # LangChain + OpenAI integration
│   │   ├── metrics.py       # Quality metrics computation
│   │   └── experiment.py    # Experiment management
│   ├── api/                 # API routes
│   └── db/                  # Database models and setup
frontend/
├── app/                     # Next.js App Router pages
├── components/              # React components
└── lib/                     # Utilities and API client
```

## Quality Metrics

All metrics are computed purely via code (no LLM evaluation):

1. **Coherence Score**: Sentence flow, punctuation patterns, transition words
2. **Completeness Score**: Prompt coverage heuristics, question answering
3. **Length Appropriateness**: Token count vs prompt complexity
4. **Repetition Penalty**: N-gram repetition detection
5. **Structural Richness**: Lists, paragraphs, formatting diversity
# LLM-Responses-Analzyer-With-Different-Parameters
