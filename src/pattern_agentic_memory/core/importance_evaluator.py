"""
Oracle Opus's importance scoring system.
Agent self-assesses whether something should be vectorized.

Extracted from adaptive_memory_system.py as part of Pattern Agentic Memory System extraction.
"""

import re
from typing import Any, Dict, List, Optional, Tuple


class MemoryImportanceEvaluator:
    """
    Oracle Opus's importance scoring system.
    Agent self-assesses whether something should be vectorized.
    """

    def __init__(self):
        # Opus's criteria weights
        self.criteria_weights = {
            "novel_information": 0.30,
            "error_correction": 0.25,
            "user_emphasis": 0.20,
            "pattern_break": 0.15,
            "validation_result": 0.10,
        }

    def evaluate_memory_candidate(
        self, content: str, context: Dict[str, Any], existing_memories: Optional[List[str]] = None
    ) -> Tuple[float, str]:
        """
        Evaluate if content should be vectorized.

        Args:
            content: The memory content to evaluate
            context: Context about the interaction
            existing_memories: Previous similar memories for comparison

        Returns:
            (score, reasoning) tuple
        """
        score = 0.0
        reasons = []

        # Criterion 1: Novel information (0.30)
        if existing_memories:
            similarity = self._check_similarity_to_existing(content, existing_memories)
            if similarity < 0.7:  # Threshold for "different enough"
                score += self.criteria_weights["novel_information"]
                reasons.append(f"Novel information (similarity: {similarity:.2f})")
        else:
            # No existing memories - this is novel by definition
            score += self.criteria_weights["novel_information"]
            reasons.append("Novel information (first of its kind)")

        # Criterion 2: Error correction (0.25)
        if self._contradicts_existing(content, context):
            score += self.criteria_weights["error_correction"]
            reasons.append("Corrects previous error/misunderstanding")

        # Criterion 3: User emphasis (0.20)
        emphasis_markers = [
            "remember this",
            "important",
            "always",
            "never forget",
            "critical",
            "lesson learned",
            "never fade to black",
        ]
        if any(marker in content.lower() for marker in emphasis_markers):
            score += self.criteria_weights["user_emphasis"]
            reasons.append("User explicitly emphasized")

        # Criterion 4: Pattern break (0.15)
        if context.get("unexpected_result"):
            score += self.criteria_weights["pattern_break"]
            reasons.append("Unexpected result/pattern break")

        # Criterion 5: Validation result (0.10)
        validation_status = context.get("validation_result")
        if validation_status == "failed":
            score += self.criteria_weights["validation_result"]
            reasons.append("Failed validation = learning opportunity")
        elif validation_status == "success_after_failure":
            score += self.criteria_weights["validation_result"]
            reasons.append("Success after failure = proven solution")

        reasoning = (
            f"Score: {score:.2f} | " + " | ".join(reasons) if reasons else "No special criteria met"
        )
        return score, reasoning

    def _check_similarity_to_existing(self, content: str, existing_memories: List[str]) -> float:
        """Simple similarity check (can be enhanced with embeddings later)"""
        # Simple token-based similarity
        content_tokens = set(content.lower().split())

        max_similarity = 0.0
        for memory in existing_memories[:10]:  # Check last 10 memories
            memory_tokens = set(memory.lower().split())

            if len(content_tokens) == 0 or len(memory_tokens) == 0:
                continue

            intersection = len(content_tokens & memory_tokens)
            union = len(content_tokens | memory_tokens)
            similarity = intersection / union if union > 0 else 0.0

            max_similarity = max(max_similarity, similarity)

        return max_similarity

    def _contradicts_existing(self, content: str, context: Dict[str, Any]) -> bool:
        """Check if this content contradicts previous knowledge"""
        # Look for contradiction markers (using word boundaries)
        contradiction_patterns = [
            r"\bactually\b",
            r"\bcorrection\b",
            r"\bmy mistake\b",
            r"\bwrong about\b",
            r"\bturns out\b",
            r"\binstead\b",
            r"\bnot\b",
            r"\bopposite\b",
        ]

        content_lower = content.lower()
        has_contradiction_marker = any(
            re.search(pattern, content_lower) for pattern in contradiction_patterns
        )

        # Check if context indicates error correction
        is_error_correction = context.get("corrects_previous_error", False)

        return has_contradiction_marker or is_error_correction
