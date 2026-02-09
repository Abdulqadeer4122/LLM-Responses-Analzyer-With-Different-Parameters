"""Custom quality metrics computed purely via code (no LLM evaluation)."""
import re
from typing import Dict, List
import math


class QualityMetricsCalculator:
    """Computes quality metrics for LLM responses."""
    
    @staticmethod
    def calculate_all(response_text: str, prompt: str, tokens_used: int = None) -> Dict[str, float]:
        """
        Calculate all quality metrics for a response.
        
        Returns a dictionary with all metric scores (0-1 range).
        """
        metrics = {
            "coherence_score": QualityMetricsCalculator._coherence_score(response_text),
            "completeness_score": QualityMetricsCalculator._completeness_score(response_text, prompt),
            "length_appropriateness": QualityMetricsCalculator._length_appropriateness(response_text, prompt, tokens_used),
            "repetition_penalty": QualityMetricsCalculator._repetition_penalty(response_text),
            "structural_richness": QualityMetricsCalculator._structural_richness(response_text),
        }
        
        # Calculate overall weighted score
        weights = {
            "coherence_score": 0.25,
            "completeness_score": 0.30,
            "length_appropriateness": 0.15,
            "repetition_penalty": 0.15,
            "structural_richness": 0.15,
        }
        
        metrics["overall_score"] = sum(
            metrics[key] * weights[key] for key in weights
        )
        
        return metrics
    
    @staticmethod
    def _coherence_score(text: str) -> float:
        """
        Measures sentence flow and punctuation quality.
        
        Rationale:
        - Proper sentence endings (., !, ?)
        - Transition words indicate flow
        - Balanced sentence lengths
        - Proper capitalization
        
        Formula: Weighted combination of punctuation patterns, transitions, and structure.
        """
        if not text or len(text.strip()) < 10:
            return 0.3
        
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 0.5
        
        score = 0.0
        
        # Punctuation quality (40% weight)
        proper_endings = sum(1 for s in sentences if s and s[-1] in '.!?')
        punctuation_score = min(proper_endings / len(sentences), 1.0) if sentences else 0.0
        score += punctuation_score * 0.4
        
        # Transition words (30% weight)
        transitions = [
            'however', 'therefore', 'furthermore', 'moreover', 'additionally',
            'consequently', 'thus', 'hence', 'meanwhile', 'subsequently',
            'nevertheless', 'nonetheless', 'accordingly', 'indeed', 'specifically'
        ]
        text_lower = text.lower()
        transition_count = sum(1 for t in transitions if t in text_lower)
        transition_score = min(transition_count / max(len(sentences) * 0.3, 1), 1.0)
        score += transition_score * 0.3
        
        # Sentence length variance (30% weight)
        # Good coherence has moderate variance (not too uniform, not too chaotic)
        if len(sentences) > 1:
            lengths = [len(s) for s in sentences]
            avg_length = sum(lengths) / len(lengths)
            variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
            # Optimal variance is around 100-400 for typical sentences
            variance_score = 1.0 - min(abs(variance - 250) / 250, 1.0)
            score += variance_score * 0.3
        
        return min(score, 1.0)
    
    @staticmethod
    def _completeness_score(text: str, prompt: str) -> float:
        """
        Measures how well the response addresses the prompt.
        
        Rationale:
        - Question words in prompt should be addressed
        - Key terms from prompt should appear in response
        - Response should be substantive (not too short)
        
        Formula: Coverage of prompt keywords and question answering.
        """
        if not text or not prompt:
            return 0.0
        
        score = 0.0
        
        # Extract question words and key terms from prompt
        question_words = ['what', 'who', 'when', 'where', 'why', 'how', 'which', 'explain', 'describe', 'list']
        prompt_lower = prompt.lower()
        text_lower = text.lower()
        
        # Question word coverage (40% weight)
        found_questions = sum(1 for qw in question_words if qw in prompt_lower)
        if found_questions > 0:
            # Check if response seems to answer (has substantial content)
            answered_score = min(len(text) / max(len(prompt) * 2, 100), 1.0)
            score += answered_score * 0.4
        
        # Keyword overlap (40% weight)
        # Extract meaningful words (3+ chars, not common stop words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        prompt_words = set(w.lower() for w in re.findall(r'\b\w{3,}\b', prompt) if w.lower() not in stop_words)
        text_words = set(w.lower() for w in re.findall(r'\b\w{3,}\b', text) if w.lower() not in stop_words)
        
        if prompt_words:
            overlap = len(prompt_words & text_words) / len(prompt_words)
            score += overlap * 0.4
        
        # Response length adequacy (20% weight)
        # Response should be at least as long as prompt (for most cases)
        length_score = min(len(text) / max(len(prompt), 50), 2.0) / 2.0  # Cap at 2x, normalize to 1.0
        score += length_score * 0.2
        
        return min(score, 1.0)
    
    @staticmethod
    def _length_appropriateness(text: str, prompt: str, tokens_used: int = None) -> float:
        """
        Measures if response length is appropriate for the prompt complexity.
        
        Rationale:
        - Simple prompts shouldn't have very long responses
        - Complex prompts should have substantial responses
        - Token usage should be reasonable
        
        Formula: Ratio of response length to prompt complexity.
        """
        if not text:
            return 0.0
        
        text_length = len(text)
        prompt_length = len(prompt)
        
        # Estimate prompt complexity (word count + question marks + exclamation marks)
        prompt_complexity = len(prompt.split()) + prompt.count('?') * 5 + prompt.count('!') * 3
        
        # Ideal response length is roughly 2-5x prompt length for most cases
        ideal_min = prompt_length * 1.5
        ideal_max = prompt_length * 8
        
        if ideal_min <= text_length <= ideal_max:
            score = 1.0
        elif text_length < ideal_min:
            # Too short
            score = text_length / ideal_min
        else:
            # Too long (but not penalized as harshly)
            excess = text_length - ideal_max
            score = max(0.5, 1.0 - (excess / ideal_max) * 0.5)
        
        # Factor in token usage if available
        if tokens_used:
            # Penalize if tokens used is very high relative to text length (inefficient)
            chars_per_token = text_length / tokens_used if tokens_used > 0 else 4
            if chars_per_token < 2:  # Very inefficient
                score *= 0.8
        
        return min(score, 1.0)
    
    @staticmethod
    def _repetition_penalty(text: str) -> float:
        """
        Detects repetition in the response (lower score = more repetition).
        
        Rationale:
        - N-gram repetition indicates poor quality
        - Repeated phrases reduce information density
        
        Formula: Inverse of repetition ratio (higher is better, so we invert).
        Returns a score where 1.0 = no repetition, 0.0 = high repetition.
        """
        if not text or len(text) < 20:
            return 0.7
        
        words = text.lower().split()
        if len(words) < 5:
            return 0.8
        
        # Check for 3-gram repetition
        n = 3
        ngrams = []
        for i in range(len(words) - n + 1):
            ngram = tuple(words[i:i+n])
            ngrams.append(ngram)
        
        if not ngrams:
            return 0.8
        
        unique_ngrams = len(set(ngrams))
        repetition_ratio = 1.0 - (unique_ngrams / len(ngrams))
        
        # Also check for repeated sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip().lower() for s in sentences if len(s.strip()) > 10]
        if len(sentences) > 1:
            unique_sentences = len(set(sentences))
            sentence_repetition = 1.0 - (unique_sentences / len(sentences))
            repetition_ratio = max(repetition_ratio, sentence_repetition * 0.7)
        
        # Convert to score (invert: high repetition = low score)
        score = 1.0 - min(repetition_ratio, 0.8)  # Cap penalty at 0.8
        return max(score, 0.2)  # Minimum score of 0.2
    
    @staticmethod
    def _structural_richness(text: str) -> float:
        """
        Measures formatting and structural diversity.
        
        Rationale:
        - Lists, paragraphs, formatting indicate thoughtful structure
        - Variety in structure improves readability
        
        Formula: Presence of lists, paragraphs, formatting markers.
        """
        if not text:
            return 0.0
        
        score = 0.0
        
        # Paragraph breaks (30% weight)
        paragraphs = text.split('\n\n')
        if len(paragraphs) > 1:
            paragraph_score = min(len(paragraphs) / 5.0, 1.0)  # Optimal around 3-5 paragraphs
            score += paragraph_score * 0.3
        else:
            # Single paragraph is okay but not ideal
            score += 0.1
        
        # List detection (30% weight)
        # Check for numbered lists, bullet points, dashes
        list_patterns = [
            r'\n\s*\d+[\.\)]\s+',  # Numbered lists
            r'\n\s*[-•*]\s+',      # Bullet points
            r'\n\s*[a-z][\.\)]\s+', # Lettered lists
        ]
        list_count = sum(len(re.findall(pattern, text)) for pattern in list_patterns)
        if list_count > 0:
            list_score = min(list_count / 3.0, 1.0)
            score += list_score * 0.3
        
        # Formatting markers (20% weight)
        formatting_markers = ['**', '*', '_', '`', '#']  # Markdown-style
        formatting_count = sum(text.count(marker) for marker in formatting_markers)
        formatting_score = min(formatting_count / 5.0, 1.0)
        score += formatting_score * 0.2
        
        # Sentence variety (20% weight)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) > 1:
            # Check for variety in sentence starters
            starters = [s.split()[0].lower() if s.split() else '' for s in sentences[:10]]
            unique_starters = len(set(starters))
            variety_score = min(unique_starters / max(len(sentences), 5), 1.0)
            score += variety_score * 0.2
        
        return min(score, 1.0)
