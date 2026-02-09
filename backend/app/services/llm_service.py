"""LangChain integration for OpenAI LLM calls."""
import asyncio
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.callbacks import get_openai_callback
import os
from dotenv import load_dotenv

load_dotenv()


class LLMService:
    """Service for managing LLM calls via LangChain."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    async def generate_response(
        self,
        prompt: str,
        temperature: float = 0.7,
        top_p: float = 1.0,
        max_tokens: int = 1000,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        model: str = "gpt-3.5-turbo"
    ) -> Dict[str, Any]:
        """
        Generate a single LLM response with specified parameters.
        
        Returns:
            Dictionary with 'text' and 'tokens_used' keys.
        """
        # Use LangChain's ChatOpenAI wrapper
        # This provides:
        # - Standardized interface across LLM providers
        # - Built-in retry logic and error handling
        # - Token counting via callbacks
        # - Streaming support (if needed later)
        
        llm = ChatOpenAI(
            model_name=model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            openai_api_key=self.api_key,
        )
        
        # Use callback to track token usage
        with get_openai_callback() as cb:
            # LangChain handles the API call, retries, and error handling
            messages = [HumanMessage(content=prompt)]
            response = await asyncio.to_thread(llm.invoke, messages)
            
            tokens_used = cb.total_tokens if cb.total_tokens else None
        
        return {
            "text": response.content,
            "tokens_used": tokens_used,
        }
    
    async def generate_batch(
        self,
        prompt: str,
        parameter_combinations: List[Dict[str, float]],
        model: str = "gpt-3.5-turbo"
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple responses with different parameter combinations.
        
        Args:
            prompt: The prompt to use
            parameter_combinations: List of dicts with keys: temperature, top_p, max_tokens, 
                                   presence_penalty, frequency_penalty
            model: OpenAI model to use
        
        Returns:
            List of response dicts with 'text', 'tokens_used', and parameter values
        """
        # Create tasks for concurrent execution
        tasks = [
            self.generate_response(
                prompt=prompt,
                temperature=combo["temperature"],
                top_p=combo["top_p"],
                max_tokens=combo["max_tokens"],
                presence_penalty=combo["presence_penalty"],
                frequency_penalty=combo["frequency_penalty"],
                model=model
            )
            for combo in parameter_combinations
        ]
        
        # Execute concurrently with error handling, preserving order
        results = []
        completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(completed_tasks):
            if isinstance(result, Exception):
                # Log error but continue with other requests
                print(f"Error generating response {i}: {result}")
                results.append({
                    "text": f"Error: {str(result)}",
                    "tokens_used": None,
                    **parameter_combinations[i]
                })
            else:
                result.update(parameter_combinations[i])
                results.append(result)
        
        return results


# Why LangChain vs Raw OpenAI SDK:
# 1. Standardization: LangChain provides a consistent interface that works across
#    multiple LLM providers (OpenAI, Anthropic, etc.), making it easier to switch
#    providers or support multiple providers in the future.
# 2. Token Tracking: Built-in callbacks make it easy to track token usage without
#    manual parsing of API responses.
# 3. Error Handling: LangChain includes retry logic and better error handling
#    for common API issues (rate limits, timeouts, etc.).
# 4. Extensibility: Easy to add chains, prompt templates, or other LangChain
#    features if needed in the future (e.g., prompt versioning, A/B testing).
# 5. Future-proofing: If we need to add features like streaming, function calling,
#    or agent workflows, LangChain provides a clear path forward.
