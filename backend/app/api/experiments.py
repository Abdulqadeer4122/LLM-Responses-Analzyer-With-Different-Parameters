"""API routes for experiment management."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import csv
import io
from datetime import datetime

from app.db.database import get_db
from app.db.models import Experiment, Response
from app.models.schemas import (
    ExperimentRequest,
    ExperimentResponse,
    ExperimentSummary,
    ResponseResult,
    QualityMetrics,
    ExportFormat
)
from app.services.experiment import ExperimentService
from app.services.llm_service import LLMService
from app.services.metrics import QualityMetricsCalculator

router = APIRouter(prefix="/api/experiments", tags=["experiments"])


@router.post("/", response_model=ExperimentResponse, status_code=status.HTTP_201_CREATED)
async def create_experiment(
    request: ExperimentRequest,
    db: Session = Depends(get_db)
):
    """
    Create and run a new experiment.
    
    Validates parameter ranges, generates combinations, calls LLM,
    computes metrics, and persists results.
    """
    # Validate parameter ranges
    is_valid, error_msg = ExperimentService.validate_parameter_ranges(request)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Generate parameter combinations
    combinations = ExperimentService.generate_parameter_combinations(request)
    
    # Create experiment record
    experiment = Experiment(
        name=request.name,
        prompt=request.prompt
    )
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    
    # Generate responses
    llm_service = LLMService()
    try:
        llm_results = await llm_service.generate_batch(
            prompt=request.prompt,
            parameter_combinations=combinations,
            model=request.model
        )
    except Exception as e:
        # Clean up experiment on error
        db.delete(experiment)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating LLM responses: {str(e)}"
        )
    
    # Compute metrics and save responses
    calculator = QualityMetricsCalculator()
    for llm_result in llm_results:
        metrics_dict = calculator.calculate_all(
            response_text=llm_result["text"],
            prompt=request.prompt,
            tokens_used=llm_result.get("tokens_used")
        )
        
        response = Response(
            experiment_id=experiment.id,
            temperature=llm_result["temperature"],
            top_p=llm_result["top_p"],
            max_tokens=llm_result["max_tokens"],
            presence_penalty=llm_result["presence_penalty"],
            frequency_penalty=llm_result["frequency_penalty"],
            response_text=llm_result["text"],
            tokens_used=llm_result.get("tokens_used"),
            metrics=metrics_dict
        )
        db.add(response)
    
    db.commit()
    db.refresh(experiment)
    
    # Return experiment with responses
    return _experiment_to_response(experiment)


@router.get("/", response_model=List[ExperimentSummary])
def list_experiments(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List all experiments with summary information."""
    experiments = db.query(Experiment).offset(skip).limit(limit).all()
    
    return [
        ExperimentSummary(
            id=exp.id,
            name=exp.name,
            prompt=exp.prompt[:100] + "..." if len(exp.prompt) > 100 else exp.prompt,
            created_at=exp.created_at,
            response_count=len(exp.responses)
        )
        for exp in experiments
    ]


@router.get("/{experiment_id}", response_model=ExperimentResponse)
def get_experiment(
    experiment_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific experiment with all responses."""
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment {experiment_id} not found"
        )
    
    return _experiment_to_response(experiment)


@router.delete("/{experiment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experiment(
    experiment_id: int,
    db: Session = Depends(get_db)
):
    """Delete an experiment and all its responses."""
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment {experiment_id} not found"
        )
    
    db.delete(experiment)
    db.commit()
    
    return None


@router.get("/{experiment_id}/export")
def export_experiment(
    experiment_id: int,
    format: str = "json",
    db: Session = Depends(get_db)
):
    """
    Export experiment data in JSON or CSV format.
    
    JSON: Complete experiment structure with all metadata.
    CSV: Tabular format with one row per response.
    """
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment {experiment_id} not found"
        )
    
    if format == "json":
        return _experiment_to_response(experiment).model_dump()
    
    elif format == "csv":
        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Response ID",
            "Temperature",
            "Top P",
            "Max Tokens",
            "Presence Penalty",
            "Frequency Penalty",
            "Response Text",
            "Tokens Used",
            "Coherence Score",
            "Completeness Score",
            "Length Appropriateness",
            "Repetition Penalty",
            "Structural Richness",
            "Overall Score",
            "Created At"
        ])
        
        # Rows
        for resp in experiment.responses:
            metrics = resp.metrics or {}
            writer.writerow([
                resp.id,
                resp.temperature,
                resp.top_p,
                resp.max_tokens,
                resp.presence_penalty,
                resp.frequency_penalty,
                resp.response_text.replace('\n', ' ').replace('\r', ' '),
                resp.tokens_used or "",
                metrics.get("coherence_score", ""),
                metrics.get("completeness_score", ""),
                metrics.get("length_appropriateness", ""),
                metrics.get("repetition_penalty", ""),
                metrics.get("structural_richness", ""),
                metrics.get("overall_score", ""),
                resp.created_at.isoformat() if resp.created_at else ""
            ])
        
        from fastapi.responses import Response as FastAPIResponse
        return FastAPIResponse(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=experiment_{experiment_id}.csv"}
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}. Use 'json' or 'csv'."
        )


def _experiment_to_response(experiment: Experiment) -> ExperimentResponse:
    """Convert database Experiment to API response model."""
    responses = [
        ResponseResult(
            id=resp.id,
            temperature=resp.temperature,
            top_p=resp.top_p,
            max_tokens=resp.max_tokens,
            presence_penalty=resp.presence_penalty,
            frequency_penalty=resp.frequency_penalty,
            response_text=resp.response_text,
            tokens_used=resp.tokens_used,
            metrics=QualityMetrics(**resp.metrics) if resp.metrics else QualityMetrics(
                coherence_score=0.0,
                completeness_score=0.0,
                length_appropriateness=0.0,
                repetition_penalty=0.0,
                structural_richness=0.0,
                overall_score=0.0
            ),
            created_at=resp.created_at
        )
        for resp in experiment.responses
    ]
    
    return ExperimentResponse(
        id=experiment.id,
        name=experiment.name,
        prompt=experiment.prompt,
        created_at=experiment.created_at,
        responses=responses
    )
