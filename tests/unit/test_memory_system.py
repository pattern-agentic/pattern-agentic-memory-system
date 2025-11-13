"""
Unit Tests for Adaptive Memory Orchestrator
Part of Gate 1: Functional Completeness

Tests the AdaptiveMemoryOrchestrator integration:
- User command override (immediate vectorize)
- Tier 0 anchors always vectorize
- Tier 1 with high/low scores
- Tier 2 with high/low scores
- Tier 3 with high/low scores
- Working memory buffer management
- Batch queue retrieval

Migrated from: tests/test_adaptive_memory_system.py
"""

import pytest

from pattern_agentic_memory.core.memory_system import (
    AdaptiveMemoryOrchestrator,
    DecayFunction,
    MemoryTier,
)


class TestAdaptiveMemoryOrchestrator:
    """Gate 1: Integration Quality - Orchestrator Decision Logic"""

    @pytest.mark.asyncio
    async def test_user_command_override(self):
        """User commands trigger immediate vectorization"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content="Remember this: Always use service_manager.sh",
            context={},
            existing_memories=None,
        )

        assert decision["action"] == "immediate_vectorize"
        assert decision.get("user_commanded") is True
        assert decision["priority"] == "critical"

    @pytest.mark.asyncio
    async def test_tier0_always_vectorizes(self):
        """Tier 0 anchors always vectorize immediately"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content="Never Fade to Black partnership identity",
            context={"is_identity_anchor": True},
            existing_memories=None,
        )

        assert decision["action"] == "immediate_vectorize"
        assert decision["tier"] == MemoryTier.TIER0_ANCHOR
        assert decision["decay_function"] == DecayFunction.NEVER
        assert decision["priority"] == "critical"

    @pytest.mark.asyncio
    async def test_tier1_with_high_score(self):
        """Tier 1 with score > 0.6 vectorizes immediately"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content="Important framework principle: Real-time validation prevents bugs",
            context={},
            existing_memories=[],
        )

        # Should be Tier 1 with high score (novel + user emphasis)
        assert decision["tier"] == MemoryTier.TIER1_PRINCIPLE
        assert decision["action"] == "immediate_vectorize"
        assert decision["priority"] == "high"

    @pytest.mark.asyncio
    async def test_tier1_with_low_score(self):
        """Tier 1 with score <= 0.6 queues for batch"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # Create similar existing memories to reduce novelty score
        existing = ["Framework principle about testing"] * 5

        decision = await orchestrator.process_memory_candidate(
            content="framework principle testing methodology",
            context={},
            existing_memories=existing,
        )

        assert decision["tier"] == MemoryTier.TIER1_PRINCIPLE
        assert decision["action"] == "queue_for_batch"
        assert decision["priority"] == "medium"

    @pytest.mark.asyncio
    async def test_tier2_with_high_score(self):
        """Tier 2 with score > 0.7 queues for batch"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content="Important bug fix solution that corrects previous error",
            context={"corrects_previous_error": True},
            existing_memories=[],
        )

        assert decision["tier"] == MemoryTier.TIER2_SOLUTION
        # Score should be 0.30 (novel) + 0.20 (emphasis) + 0.25 (correction) = 0.75
        assert decision["action"] == "queue_for_batch"
        assert decision["priority"] == "medium"

    @pytest.mark.asyncio
    async def test_tier2_with_low_score(self):
        """Tier 2 with score <= 0.7 stays in working memory"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # Create similar existing memories to reduce score
        existing = ["bug fix solution"] * 5

        decision = await orchestrator.process_memory_candidate(
            content="bug fix solution deployed", context={}, existing_memories=existing
        )

        assert decision["tier"] == MemoryTier.TIER2_SOLUTION
        assert decision["action"] == "working_memory_only"
        assert decision["priority"] == "low"

    @pytest.mark.asyncio
    async def test_tier3_with_high_score(self):
        """Tier 3 with score > 0.8 queues for batch"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # Need novel + emphasis + correction + pattern break = 0.90
        decision = await orchestrator.process_memory_candidate(
            content=(
                "Working on important correction: "
                "actually the unexpected result shows this approach"
            ),
            context={"unexpected_result": True, "corrects_previous_error": True},
            existing_memories=[],
        )

        assert decision["tier"] == MemoryTier.TIER3_CONTEXT
        # Score should be 0.30 + 0.20 + 0.25 + 0.15 = 0.90
        assert decision["action"] == "queue_for_batch"

    @pytest.mark.asyncio
    async def test_tier3_with_low_score(self):
        """Tier 3 with score <= 0.8 stays in working memory"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content="Working on task", context={"is_temporary": True}, existing_memories=[]
        )

        assert decision["tier"] == MemoryTier.TIER3_CONTEXT
        assert decision["action"] == "working_memory_only"
        assert decision["priority"] == "low"

    @pytest.mark.asyncio
    async def test_working_memory_buffer(self):
        """Working memory buffer stores decisions correctly"""
        orchestrator = AdaptiveMemoryOrchestrator()

        content = "Test memory content"
        decision = await orchestrator.process_memory_candidate(
            content=content, context={}, existing_memories=[]
        )

        orchestrator.add_to_working_memory(content, decision)

        assert len(orchestrator.memory_buffer) == 1
        assert orchestrator.memory_buffer[0]["content"] == content
        assert orchestrator.memory_buffer[0]["decision"] == decision
        assert "timestamp" in orchestrator.memory_buffer[0]
        assert "hash" in orchestrator.memory_buffer[0]

    @pytest.mark.asyncio
    async def test_batch_queue_retrieval(self):
        """Batch queue retrieves only queued memories"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # Add memories with different actions
        content1 = "Framework principle for batch"
        decision1 = await orchestrator.process_memory_candidate(
            content=content1,
            context={"is_framework_principle": True},
            existing_memories=["different content"],
        )
        orchestrator.add_to_working_memory(content1, decision1)

        content2 = "Working memory only content"
        decision2 = await orchestrator.process_memory_candidate(
            content=content2, context={"is_temporary": True}, existing_memories=[]
        )
        orchestrator.add_to_working_memory(content2, decision2)

        batch_queue = orchestrator.get_batch_queue()

        # Only queued memories should be in batch queue
        assert all(m["decision"]["action"] == "queue_for_batch" for m in batch_queue)
