# LLM Lab - Quick Start Guide

## Prerequisites

- Python 3.8+
- Node.js 18+
- OpenAI API key

## Quick Setup

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=your_key_here
uvicorn app.main:app --reload
```

Backend runs on `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

## Usage

1. **Enter a prompt** in the Prompt Editor
2. **Configure parameters** (use range toggle to test multiple values)
3. **Select a model** (GPT-3.5 Turbo, GPT-4, etc.)
4. **Click "Run Experiment"**
5. **View results** in the comparison grid
6. **Click any response** to see detailed metrics
7. **Export** results as JSON or CSV

## Example Experiment

Try this prompt with temperature range:
- Prompt: "Explain the concept of machine learning in 3 sentences"
- Temperature: Min 0.5, Max 1.0, Step 0.1
- This will generate 6 responses with different creativity levels

## Understanding Metrics

- **Coherence Score**: Sentence flow and punctuation quality
- **Completeness Score**: How well the response addresses the prompt
- **Length Appropriateness**: Whether response length matches prompt complexity
- **Repetition Penalty**: Detects repetitive content (lower = more repetition)
- **Structural Richness**: Formatting, lists, and structural diversity
- **Overall Score**: Weighted average of all metrics

## Troubleshooting

**Backend errors:**
- Check that `OPENAI_API_KEY` is set in `.env`
- Ensure port 8000 is available
- Check Python version (3.8+)

**Frontend errors:**
- Ensure backend is running on port 8000
- Check browser console for API errors
- Verify `NEXT_PUBLIC_API_URL` if using custom backend URL

**API rate limits:**
- Reduce parameter combinations (max 50)
- Use smaller step sizes or fewer ranges
- Consider using GPT-3.5 Turbo instead of GPT-4 for testing
