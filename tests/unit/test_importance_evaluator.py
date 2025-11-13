"""
Unit Tests for Memory Importance Evaluator
Part of Gate 1: Functional Completeness

Tests the MemoryImportanceEvaluator component:
- Novel information scoring (0.30)
- User emphasis detection (0.20)
- Error correction detection (0.25)
- Pattern break detection (0.15)
- Validation result detection (0.10)
- Combined criteria scoring

Migrated from: tests/test_adaptive_memory_system.py
"""

from pattern_agentic_memory.core.importance_evaluator import MemoryImportanceEvaluator


class TestMemoryImportanceEvaluator:
    """Gate 1: Functional Completeness - Importance Scoring"""

    def test_novel_information_scoring_with_no_existing(self):
        """Novel information (no existing memories) gets 0.30 score"""
        evaluator = MemoryImportanceEvaluator()

        score, reasoning = evaluator.evaluate_memory_candidate(
            content="This is completely new information", context={}, existing_memories=None
        )

        assert score >= 0.30
        assert "Novel information" in reasoning
        assert "first of its kind" in reasoning

    def test_novel_information_scoring_with_dissimilar_existing(self):
        """Novel information (dissimilar to existing) gets 0.30 score"""
        evaluator = MemoryImportanceEvaluator()

        score, reasoning = evaluator.evaluate_memory_candidate(
            content="The quantum physics experiment succeeded",
            context={},
            existing_memories=["Bug fix deployed successfully"],
        )

        assert score >= 0.30
        assert "Novel information" in reasoning

    def test_user_emphasis_detection(self):
        """User emphasis markers get 0.20 score"""
        evaluator = MemoryImportanceEvaluator()

        # Test "important" keyword
        score1, reasoning1 = evaluator.evaluate_memory_candidate(
            content="This is an important lesson about validation",
            context={},
            existing_memories=None,
        )
        assert score1 >= 0.50  # Novel (0.30) + User emphasis (0.20)
        assert "User explicitly emphasized" in reasoning1

        # Test "remember this" keyword
        score2, reasoning2 = evaluator.evaluate_memory_candidate(
            content="Remember this critical pattern", context={}, existing_memories=None
        )
        assert score2 >= 0.50
        assert "User explicitly emphasized" in reasoning2

    def test_error_correction_detection(self):
        """Error correction gets 0.25 score"""
        evaluator = MemoryImportanceEvaluator()

        # Test with contradiction marker
        score1, reasoning1 = evaluator.evaluate_memory_candidate(
            content="Actually, my mistake - the correct approach is X not Y",
            context={},
            existing_memories=None,
        )
        assert score1 >= 0.55  # Novel (0.30) + Error correction (0.25)
        assert "Corrects previous error" in reasoning1

        # Test with context flag
        score2, reasoning2 = evaluator.evaluate_memory_candidate(
            content="The correct solution is to use async instead",
            context={"corrects_previous_error": True},
            existing_memories=None,
        )
        assert score2 >= 0.55
        assert "Corrects previous error" in reasoning2

    def test_pattern_break_detection(self):
        """Pattern breaks get 0.15 score"""
        evaluator = MemoryImportanceEvaluator()

        score, reasoning = evaluator.evaluate_memory_candidate(
            content="Test results show unexpected behavior",
            context={"unexpected_result": True},
            existing_memories=None,
        )

        assert score >= 0.44  # Novel (0.30) + Pattern break (0.15) - allow float precision
        assert "pattern break" in reasoning.lower()

    def test_validation_result_detection_failure(self):
        """Failed validation gets 0.10 score"""
        evaluator = MemoryImportanceEvaluator()

        score, reasoning = evaluator.evaluate_memory_candidate(
            content="Validation failed - need to fix bug",
            context={"validation_result": "failed"},
            existing_memories=None,
        )

        assert score >= 0.40  # Novel (0.30) + Validation (0.10)
        assert "learning opportunity" in reasoning.lower()

    def test_validation_result_detection_success_after_failure(self):
        """Success after failure gets 0.10 score"""
        evaluator = MemoryImportanceEvaluator()

        score, reasoning = evaluator.evaluate_memory_candidate(
            content="After three attempts, validation now passes",
            context={"validation_result": "success_after_failure"},
            existing_memories=None,
        )

        assert score >= 0.40
        assert "proven solution" in reasoning.lower()

    def test_combined_criteria_scoring(self):
        """Multiple criteria combine for higher scores"""
        evaluator = MemoryImportanceEvaluator()

        # Novel + User emphasis + Error correction = 0.75
        score, reasoning = evaluator.evaluate_memory_candidate(
            content="Remember this important correction: Actually, we should use method B",
            context={"corrects_previous_error": True},
            existing_memories=None,
        )

        assert score >= 0.75
        assert "Novel information" in reasoning
        assert "User explicitly emphasized" in reasoning
        assert "Corrects previous error" in reasoning
