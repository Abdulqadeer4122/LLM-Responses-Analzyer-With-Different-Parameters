"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base
from app.api.experiments import router as experiments_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LLM Lab API",
    description="API for experimenting with LLM parameters and analyzing response quality",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", 'https://llm-responses-analzyer-with-different.onrender.com'],  # Next.js default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(experiments_router)


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "LLM Lab API is running"}


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}
