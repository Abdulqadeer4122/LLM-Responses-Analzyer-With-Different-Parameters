"""Experiment management and parameter combination generation."""
from typing import List, Dict, Any, Optional
from app.models.schemas import ParameterRange, ExperimentRequest
import itertools


class ExperimentService:
    """Service for managing experiments and generating parameter combinations."""
    
    @staticmethod
    def generate_parameter_combinations(request: ExperimentRequest) -> List[Dict[str, float]]:
        """
        Generate all parameter combinations from ranges.
        
        Args:
            request: ExperimentRequest with parameter ranges
        
        Returns:
            List of parameter combination dicts
        """
        # Helper to get values from a ParameterRange
        def get_values(param_range: Optional[ParameterRange], default: float) -> List[float]:
            if param_range is None:
                return [default]
            
            if param_range.values:
                return param_range.values
            
            if param_range.step:
                values = []
                current = param_range.min
                while current <= param_range.max:
                    values.append(round(current, 3))
                    current += param_range.step
                return values if values else [default]
            
            # If no step, use min and max
            return [param_range.min, param_range.max] if param_range.min != param_range.max else [param_range.min]
        
        # Get all parameter values
        temperatures = get_values(request.temperature, 0.7)
        top_ps = get_values(request.top_p, 1.0)
        max_tokens_list = [int(v) for v in get_values(request.max_tokens, 1000)]
        presence_penalties = get_values(request.presence_penalty, 0.0)
        frequency_penalties = get_values(request.frequency_penalty, 0.0)
        
        # Generate all combinations
        combinations = list(itertools.product(
            temperatures,
            top_ps,
            max_tokens_list,
            presence_penalties,
            frequency_penalties
        ))
        
        # Convert to list of dicts
        result = [
            {
                "temperature": combo[0],
                "top_p": combo[1],
                "max_tokens": combo[2],
                "presence_penalty": combo[3],
                "frequency_penalty": combo[4],
            }
            for combo in combinations
        ]
        
        return result
    
    @staticmethod
    def validate_parameter_ranges(request: ExperimentRequest) -> tuple[bool, Optional[str]]:
        """
        Validate parameter ranges to prevent excessive combinations.
        
        Returns:
            (is_valid, error_message)
        """
        # Estimate number of combinations
        def count_values(param_range: Optional[ParameterRange], default: float) -> int:
            if param_range is None:
                return 1
            if param_range.values:
                return len(param_range.values)
            if param_range.step:
                count = int((param_range.max - param_range.min) / param_range.step) + 1
                return max(count, 1)
            return 2 if param_range.min != param_range.max else 1
        
        total_combinations = (
            count_values(request.temperature, 0.7) *
            count_values(request.top_p, 1.0) *
            count_values(request.max_tokens, 1000) *
            count_values(request.presence_penalty, 0.0) *
            count_values(request.frequency_penalty, 0.0)
        )
        
        # Limit to prevent excessive API calls and costs
        MAX_COMBINATIONS = 50
        
        if total_combinations > MAX_COMBINATIONS:
            return False, f"Too many parameter combinations ({total_combinations}). Maximum allowed is {MAX_COMBINATIONS}. Please reduce the ranges or step sizes."
        
        return True, None
