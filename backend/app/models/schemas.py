"""Pydantic schemas for API request/response validation."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class ParameterRange(BaseModel):
    """Defines a range for a single parameter."""
    min: float = Field(..., ge=0, description="Minimum value")
    max: float = Field(..., ge=0, description="Maximum value")
    step: Optional[float] = Field(None, description="Step size for generation")
    values: Optional[List[float]] = Field(None, description="Specific values to use (overrides min/max/step)")

    @field_validator('max')
    def max_greater_than_min(cls, v, info):
        if 'min' in info.data and v < info.data['min']:
            raise ValueError('max must be greater than or equal to min')
        return v


class ExperimentRequest(BaseModel):
    """Request to create and run an experiment."""
    prompt: str = Field(..., min_length=1, description="The prompt to send to the LLM")
    name: Optional[str] = Field(None, max_length=255, description="Optional experiment name")
    
    # Parameter ranges
    temperature: Optional[ParameterRange] = Field(None, description="Temperature range (default: single value 0.7)")
    top_p: Optional[ParameterRange] = Field(None, description="Top-p range (default: single value 1.0)")
    max_tokens: Optional[ParameterRange] = Field(None, description="Max tokens range (default: single value 1000)")
    presence_penalty: Optional[ParameterRange] = Field(None, description="Presence penalty range (default: single value 0.0)")
    frequency_penalty: Optional[ParameterRange] = Field(None, description="Frequency penalty range (default: single value 0.0)")
    
    model: str = Field(default="gpt-3.5-turbo", description="OpenAI model to use")


class QualityMetrics(BaseModel):
    """Quality metrics computed for a response."""
    coherence_score: float = Field(..., ge=0, le=1, description="Sentence flow and punctuation quality")
    completeness_score: float = Field(..., ge=0, le=1, description="Prompt coverage and completeness")
    length_appropriateness: float = Field(..., ge=0, le=1, description="Token count appropriateness")
    repetition_penalty: float = Field(..., ge=0, le=1, description="Repetition detection (lower is better, inverted)")
    structural_richness: float = Field(..., ge=0, le=1, description="Formatting and structure diversity")
    overall_score: float = Field(..., ge=0, le=1, description="Weighted average of all metrics")


class ResponseResult(BaseModel):
    """Single LLM response with parameters and metrics."""
    id: int
    temperature: float
    top_p: float
    max_tokens: int
    presence_penalty: float
    frequency_penalty: float
    response_text: str
    tokens_used: Optional[int]
    metrics: QualityMetrics
    created_at: datetime


class ExperimentResponse(BaseModel):
    """Complete experiment with all responses."""
    id: int
    name: Optional[str]
    prompt: str
    created_at: datetime
    responses: List[ResponseResult]


class ExperimentSummary(BaseModel):
    """Summary of an experiment for listing."""
    id: int
    name: Optional[str]
    prompt: str
    created_at: datetime
    response_count: int


class ExportFormat(BaseModel):
    """Export format specification."""
    format: str = Field(..., pattern="^(json|csv)$", description="Export format: json or csv")
