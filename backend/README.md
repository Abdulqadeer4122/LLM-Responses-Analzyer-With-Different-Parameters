# LLM Lab Backend

FastAPI backend for LLM Lab application.

## Setup

1. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

4. **Run the server**:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database

By default, the application uses SQLite (`llm_lab.db`). To use PostgreSQL:

1. Update `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost/llm_lab
```

2. Install PostgreSQL adapter:
```bash
pip install psycopg2-binary
```

## Testing

Example API call:

```bash
curl -X POST "http://localhost:8000/api/experiments/" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing in simple terms",
    "name": "Quantum Computing Test",
    "temperature": {"min": 0.7, "max": 0.9, "step": 0.1},
    "model": "gpt-3.5-turbo"
  }'
```

## Project Structure

- `app/main.py`: FastAPI application entry point
- `app/models/schemas.py`: Pydantic models for validation
- `app/services/`: Business logic
  - `llm_service.py`: LangChain + OpenAI integration
  - `metrics.py`: Quality metrics computation
  - `experiment.py`: Parameter combination generation
- `app/api/experiments.py`: API route handlers
- `app/db/`: Database models and configuration
