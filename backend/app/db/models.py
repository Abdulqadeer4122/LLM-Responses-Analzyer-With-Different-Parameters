"""Database models for experiments and responses."""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Experiment(Base):
    """Stores experiment metadata."""
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    prompt = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    responses = relationship("Response", back_populates="experiment", cascade="all, delete-orphan")


class Response(Base):
    """Stores individual LLM responses with parameters and metrics."""
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False)
    
    # LLM Parameters
    temperature = Column(Float, nullable=False)
    top_p = Column(Float, nullable=False)
    max_tokens = Column(Integer, nullable=False)
    presence_penalty = Column(Float, nullable=False)
    frequency_penalty = Column(Float, nullable=False)
    
    # Response data
    response_text = Column(Text, nullable=False)
    tokens_used = Column(Integer, nullable=True)
    
    # Quality metrics (stored as JSON for flexibility)
    metrics = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    experiment = relationship("Experiment", back_populates="responses")
