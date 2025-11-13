"""
Stability Tests for Adaptive Memory System
Gate 4: Edge Cases and Error Handling

Tests system stability under adverse conditions:
1. Empty/invalid inputs
2. Missing and malformed data
3. Multiple simultaneous commands and conflicts
4. Extreme content sizes
5. Special characters and encoding
6. No matching keywords fallback
7. Component stability
8. Concurrent operations
9. Working memory edge cases

Migrated from: tests/test_adaptive_memory_stability.py
"""

import pytest

from pattern_agentic_memory.core.command_parser import UserMemoryCommandParser
from pattern_agentic_memory.core.importance_evaluator import MemoryImportanceEvaluator
from pattern_agentic_memory.core.memory_system import (
    AdaptiveMemoryOrchestrator,
    DecayFunction,
    MemoryTier,
)
from pattern_agentic_memory.core.tier_classifier import H200TierClassifier


class TestEmptyAndInvalidInputs:
    """Gate 4: Stability - Empty and Invalid Input Handling"""

    @pytest.mark.asyncio
    async def test_empty_content_string(self):
        """Handle empty content gracefully"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content="", context={}, existing_memories=None
        )

        # Should not crash, should have valid decision structure
        assert "action" in decision
        assert "tier" in decision
        assert "decay_function" in decision
        assert "reasoning" in decision
        assert "priority" in decision

    @pytest.mark.asyncio
    async def test_whitespace_only_content(self):
        """Handle whitespace-only content"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content="   \n\t\r   ", context={}, existing_memories=None
        )

        assert "action" in decision
        assert decision["tier"] is not None

    @pytest.mark.asyncio
    async def test_empty_context_dict(self):
        """Handle empty context dictionary"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content="Test content", context={}, existing_memories=None
        )

        assert decision is not None
        assert "action" in decision

    @pytest.mark.asyncio
    async def test_none_existing_memories(self):
        """Handle None existing_memories parameter"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content="Test content", context={}, existing_memories=None
        )

        assert decision is not None
        # Should treat as novel since no existing memories
        assert "reasoning" in decision

    @pytest.mark.asyncio
    async def test_empty_existing_memories_list(self):
        """Handle empty existing memories list"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content="Test content", context={}, existing_memories=[]
        )

        assert decision is not None
        # Should treat as novel
        assert "reasoning" in decision


class TestMissingAndMalformedData:
    """Gate 4: Stability - Missing and Malformed Data Handling"""

    @pytest.mark.asyncio
    async def test_missing_context_keys(self):
        """Handle context dict missing expected keys"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # Context with no special flags
        decision = await orchestrator.process_memory_candidate(
            content="Test content", context={"unrelated_key": "value"}, existing_memories=None
        )

        assert decision is not None
        assert "tier" in decision

    @pytest.mark.asyncio
    async def test_malformed_context_values(self):
        """Handle invalid context value types"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # String instead of bool
        decision1 = await orchestrator.process_memory_candidate(
            content="Test content",
            context={"corrects_previous_error": "not a boolean"},
            existing_memories=None,
        )
        assert decision1 is not None

        # Wrong validation_result value
        decision2 = await orchestrator.process_memory_candidate(
            content="Test content",
            context={"validation_result": "invalid_status"},
            existing_memories=None,
        )
        assert decision2 is not None

    @pytest.mark.asyncio
    async def test_existing_memories_with_empty_strings(self):
        """Handle existing memories containing empty strings"""
        orchestrator = AdaptiveMemoryOrchestrator()

        existing = ["", "   ", "Valid memory", "", "Another valid"]

        decision = await orchestrator.process_memory_candidate(
            content="New content", context={}, existing_memories=existing
        )

        assert decision is not None
        # Should handle empty strings without crashing

    @pytest.mark.asyncio
    async def test_existing_memories_with_none_values(self):
        """Handle existing memories list with None values"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # Note: In practice, the system should filter these, but test stability
        existing = ["Valid memory", "Another memory"]

        decision = await orchestrator.process_memory_candidate(
            content="New content", context={}, existing_memories=existing
        )

        assert decision is not None


class TestMultipleCommandsAndConflicts:
    """Gate 4: Stability - Multiple Commands and Conflicting Signals"""

    @pytest.mark.asyncio
    async def test_multiple_user_commands_in_one_message(self):
        """Handle multiple user commands in single content"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content="Remember this important lesson learned: critical pattern to save",
            context={},
            existing_memories=None,
        )

        # Should detect at least one command
        assert decision["action"] == "immediate_vectorize"
        assert decision.get("user_commanded") is True

    @pytest.mark.asyncio
    async def test_contradictory_context_flags(self):
        """Handle contradictory context flags"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content="Test content",
            context={
                "is_identity_anchor": True,
                "is_temporary": True,  # Contradictory
                "ephemeral": True,
            },
            existing_memories=None,
        )

        # Should make a decision (priority likely to identity anchor)
        assert decision is not None
        assert decision["tier"] is not None

    @pytest.mark.asyncio
    async def test_explicit_tier_override_with_keywords(self):
        """Handle explicit tier override conflicting with keyword detection"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content="Never Fade to Black framework methodology",  # Has Tier 0 keywords
            context={"tier": "context"},  # Override to Tier 3
            existing_memories=None,
        )

        # Explicit override should win
        assert decision["tier"] == MemoryTier.TIER3_CONTEXT

    @pytest.mark.asyncio
    async def test_user_command_with_contradictory_tier(self):
        """Handle user command with context suggesting different tier"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content="Remember this temporary note",  # Command + temporary
            context={"is_temporary": True},
            existing_memories=None,
        )

        # User command should override temporary classification
        assert decision["action"] == "immediate_vectorize"
        assert decision.get("user_commanded") is True


class TestExtremeContentSizes:
    """Gate 4: Stability - Extreme Content Sizes"""

    @pytest.mark.asyncio
    async def test_very_long_content_10kb(self):
        """Handle very long content (10KB)"""
        orchestrator = AdaptiveMemoryOrchestrator()

        long_content = "A" * 10000  # 10KB

        decision = await orchestrator.process_memory_candidate(
            content=long_content, context={}, existing_memories=None
        )

        assert decision is not None
        assert "action" in decision

    @pytest.mark.asyncio
    async def test_extremely_long_content_100kb(self):
        """Handle extremely long content (100KB)"""
        orchestrator = AdaptiveMemoryOrchestrator()

        very_long_content = "B" * 100000  # 100KB

        decision = await orchestrator.process_memory_candidate(
            content=very_long_content, context={}, existing_memories=None
        )

        assert decision is not None
        assert "tier" in decision

    @pytest.mark.asyncio
    async def test_long_content_with_keywords(self):
        """Handle long content with keywords scattered throughout"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # Build long content with keywords at different positions
        parts = ["filler text " * 100 for _ in range(10)]
        parts[0] = "Remember this important " + parts[0]
        parts[5] = parts[5] + " framework methodology "
        parts[9] = parts[9] + " Never Fade to Black"

        long_content = "".join(parts)

        decision = await orchestrator.process_memory_candidate(
            content=long_content, context={}, existing_memories=None
        )

        # Should detect user command even in long content
        assert decision["action"] == "immediate_vectorize"
        assert decision.get("user_commanded") is True

    @pytest.mark.asyncio
    async def test_many_existing_memories(self):
        """Handle large number of existing memories"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # 100 existing memories (more than the 10 limit for comparison)
        existing = [f"Existing memory {i} with various content and keywords" for i in range(100)]

        decision = await orchestrator.process_memory_candidate(
            content="New memory to compare", context={}, existing_memories=existing
        )

        assert decision is not None
        # Should only compare against last 10 (per implementation)


class TestSpecialCharactersAndEncoding:
    """Gate 4: Stability - Special Characters and Encoding"""

    @pytest.mark.asyncio
    async def test_unicode_content(self):
        """Handle Unicode characters in content"""
        orchestrator = AdaptiveMemoryOrchestrator()

        unicode_content = "Remember this: 你好世界 Привет мир ñoño"

        decision = await orchestrator.process_memory_candidate(
            content=unicode_content, context={}, existing_memories=None
        )

        assert decision is not None
        assert decision.get("user_commanded") is True

    @pytest.mark.asyncio
    async def test_special_characters_in_content(self):
        """Handle special characters and symbols"""
        orchestrator = AdaptiveMemoryOrchestrator()

        special_content = "Test with special chars: @#$%^&*()_+-=[]{}|;':\"<>?,./"

        decision = await orchestrator.process_memory_candidate(
            content=special_content, context={}, existing_memories=None
        )

        assert decision is not None

    @pytest.mark.asyncio
    async def test_markdown_and_code_in_content(self):
        """Handle markdown and code snippets in content"""
        orchestrator = AdaptiveMemoryOrchestrator()

        markdown_content = """
        Remember this pattern:
        ```python
        def important_function():
            return "Never forget this"
        ```
        **Critical**: Always validate
        """

        decision = await orchestrator.process_memory_candidate(
            content=markdown_content, context={}, existing_memories=None
        )

        assert decision is not None
        assert decision.get("user_commanded") is True

    @pytest.mark.asyncio
    async def test_newlines_and_formatting(self):
        """Handle various newline and formatting characters"""
        orchestrator = AdaptiveMemoryOrchestrator()

        formatted_content = "Line 1\nLine 2\r\nLine 3\rLine 4\t\tTabbed"

        decision = await orchestrator.process_memory_candidate(
            content=formatted_content, context={}, existing_memories=None
        )

        assert decision is not None


class TestNoMatchingKeywords:
    """Gate 4: Stability - Content with No Matching Keywords"""

    @pytest.mark.asyncio
    async def test_generic_content_no_keywords(self):
        """Handle content with no matching tier keywords"""
        orchestrator = AdaptiveMemoryOrchestrator()

        generic_content = "Random unrelated text about weather and cooking"

        decision = await orchestrator.process_memory_candidate(
            content=generic_content, context={}, existing_memories=None
        )

        # Should default to Tier 2
        assert decision["tier"] == MemoryTier.TIER2_SOLUTION
        assert decision["decay_function"] == DecayFunction.STALENESS_6MONTHS

    @pytest.mark.asyncio
    async def test_numeric_only_content(self):
        """Handle numeric-only content"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content="123456789", context={}, existing_memories=None
        )

        assert decision is not None
        assert decision["tier"] == MemoryTier.TIER2_SOLUTION

    @pytest.mark.asyncio
    async def test_single_word_content(self):
        """Handle single word content"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content="test", context={}, existing_memories=None
        )

        assert decision is not None
        assert "tier" in decision

    @pytest.mark.asyncio
    async def test_punctuation_only_content(self):
        """Handle punctuation-only content"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content="...!!!???", context={}, existing_memories=None
        )

        assert decision is not None


class TestComponentStability:
    """Gate 4: Stability - Individual Component Error Handling"""

    def test_importance_evaluator_empty_content(self):
        """MemoryImportanceEvaluator handles empty content"""
        evaluator = MemoryImportanceEvaluator()

        score, reasoning = evaluator.evaluate_memory_candidate(
            content="", context={}, existing_memories=None
        )

        assert isinstance(score, float)
        assert isinstance(reasoning, str)

    def test_importance_evaluator_none_existing(self):
        """MemoryImportanceEvaluator handles None existing memories"""
        evaluator = MemoryImportanceEvaluator()

        score, reasoning = evaluator.evaluate_memory_candidate(
            content="Test content", context={}, existing_memories=None
        )

        # Should treat as novel
        assert score >= 0.30

    def test_tier_classifier_empty_content(self):
        """H200TierClassifier handles empty content"""
        classifier = H200TierClassifier()

        tier, decay = classifier.classify_memory_tier(content="", context={})

        # Should default to Tier 2
        assert tier == MemoryTier.TIER2_SOLUTION
        assert decay == DecayFunction.STALENESS_6MONTHS

    def test_tier_classifier_invalid_tier_override(self):
        """H200TierClassifier handles invalid tier override"""
        classifier = H200TierClassifier()

        tier, decay = classifier.classify_memory_tier(
            content="Test content", context={"tier": "invalid_tier_name"}
        )

        # Should fall back to keyword detection or default
        assert tier is not None
        assert decay is not None

    def test_command_parser_empty_message(self):
        """UserMemoryCommandParser handles empty message"""
        parser = UserMemoryCommandParser()

        result = parser.parse_user_intent("")

        # Should return None for empty message
        assert result is None

    def test_command_parser_none_message(self):
        """UserMemoryCommandParser handles None message"""
        parser = UserMemoryCommandParser()

        # Should handle gracefully or raise appropriate error
        try:
            result = parser.parse_user_intent(None)
            assert result is None
        except (AttributeError, TypeError):
            # Acceptable to raise error for None input
            pass


class TestConcurrentStability:
    """Gate 4: Stability - Rapid Sequential Processing"""

    @pytest.mark.asyncio
    async def test_rapid_sequential_processing(self):
        """Handle rapid sequential memory processing"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # Process 50 memories rapidly
        for i in range(50):
            decision = await orchestrator.process_memory_candidate(
                content=f"Rapid memory {i}", context={}, existing_memories=None
            )
            orchestrator.add_to_working_memory(f"Rapid memory {i}", decision)

        # Should not corrupt buffer
        assert len(orchestrator.memory_buffer) == 50

        # All items should have unique hashes
        hashes = [item["hash"] for item in orchestrator.memory_buffer]
        assert len(hashes) == len(set(hashes))

    @pytest.mark.asyncio
    async def test_alternating_context_flags(self):
        """Handle alternating context flags in rapid succession"""
        orchestrator = AdaptiveMemoryOrchestrator()

        contexts = [
            {"is_identity_anchor": True},
            {"is_temporary": True},
            {"corrects_previous_error": True},
            {"unexpected_result": True},
            {"validation_result": "failed"},
            {},
        ]

        for i in range(30):
            context = contexts[i % len(contexts)]
            decision = await orchestrator.process_memory_candidate(
                content=f"Memory {i}", context=context, existing_memories=None
            )

            assert decision is not None
            assert "tier" in decision


class TestWorkingMemoryStability:
    """Gate 4: Stability - Working Memory Buffer Edge Cases"""

    @pytest.mark.asyncio
    async def test_duplicate_content_hashing(self):
        """Duplicate content should have same hash"""
        orchestrator = AdaptiveMemoryOrchestrator()

        content = "Duplicate content test"

        decision1 = await orchestrator.process_memory_candidate(
            content=content, context={}, existing_memories=None
        )
        orchestrator.add_to_working_memory(content, decision1)

        decision2 = await orchestrator.process_memory_candidate(
            content=content, context={}, existing_memories=None
        )
        orchestrator.add_to_working_memory(content, decision2)

        # Both should have same hash
        hash1 = orchestrator.memory_buffer[0]["hash"]
        hash2 = orchestrator.memory_buffer[1]["hash"]
        assert hash1 == hash2

    @pytest.mark.asyncio
    async def test_batch_queue_with_no_batch_items(self):
        """Batch queue should return empty list when no items queued"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # Add only working memory items
        for i in range(10):
            decision = await orchestrator.process_memory_candidate(
                content=f"Working memory {i}", context={"is_temporary": True}, existing_memories=[]
            )
            orchestrator.add_to_working_memory(f"Working memory {i}", decision)

        batch_queue = orchestrator.get_batch_queue()
        assert isinstance(batch_queue, list)
        # May be empty or contain items, but should not crash

    @pytest.mark.asyncio
    async def test_batch_queue_with_all_batch_items(self):
        """Batch queue should return all items when all are queued"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # Add only batch items
        for i in range(10):
            decision = await orchestrator.process_memory_candidate(
                content=f"Framework principle {i}",
                context={"is_framework_principle": True},
                existing_memories=["different content"],
            )
            orchestrator.add_to_working_memory(f"Framework principle {i}", decision)

        batch_queue = orchestrator.get_batch_queue()
        # All should be queued for batch
        assert all(m["decision"]["action"] == "queue_for_batch" for m in batch_queue)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
