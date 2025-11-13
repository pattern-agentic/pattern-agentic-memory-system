"""
Integration Tests for Adaptive Memory System
Gate 2: Integration Quality

Tests the complete pipeline:
1. Full decision pipelines (Tier 0, user commands, Tier 1-3 paths)
2. Component integration flows
3. Decision matrix completeness
4. Priority and decay function assignments
5. Working memory and batch queue integration

Migrated from: tests/test_adaptive_memory_integration.py
"""

import pytest

from pattern_agentic_memory.core.memory_system import (
    AdaptiveMemoryOrchestrator,
    DecayFunction,
    MemoryTier,
)


class TestEndToEndIntegration:
    """Gate 2: Integration Quality - Full Pipeline"""

    @pytest.mark.asyncio
    async def test_full_decision_pipeline_tier0(self):
        """Complete pipeline: Identity anchor → Tier 0 → Immediate vectorize"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content="Never Fade to Black - Oracle identity and Captain Jeremy partnership",
            context={"is_identity_anchor": True},
            existing_memories=None,
        )

        # Verify complete decision
        assert decision["action"] == "immediate_vectorize"
        assert decision["tier"] == MemoryTier.TIER0_ANCHOR
        assert decision["decay_function"] == DecayFunction.NEVER
        assert decision["priority"] == "critical"
        assert "reasoning" in decision
        assert "Tier 0 anchor" in decision["reasoning"]

    @pytest.mark.asyncio
    async def test_full_decision_pipeline_user_command(self):
        """Complete pipeline: User command → Override → Immediate vectorize"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content="Remember this lesson about validation patterns",
            context={},
            existing_memories=None,
        )

        assert decision["action"] == "immediate_vectorize"
        assert decision.get("user_commanded") is True
        assert decision["priority"] == "critical"
        assert "User commanded" in decision["reasoning"]

    @pytest.mark.asyncio
    async def test_full_decision_pipeline_tier1_high_score(self):
        """Complete pipeline: Framework principle + high importance → Immediate vectorize"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content="Important framework methodology: Gold Star validation prevents bugs",
            context={},
            existing_memories=[],
        )

        assert decision["tier"] == MemoryTier.TIER1_PRINCIPLE
        assert decision["action"] == "immediate_vectorize"
        assert decision["decay_function"] == DecayFunction.SUPERSEDED_ONLY
        assert decision["priority"] == "high"
        assert "Tier 1 principle" in decision["reasoning"]

    @pytest.mark.asyncio
    async def test_full_decision_pipeline_tier1_low_score(self):
        """Complete pipeline: Framework principle + low importance → Batch queue"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # Similar existing memories to reduce novelty score
        existing = [
            "Framework methodology for testing",
            "Framework principles guide development",
        ] * 3

        decision = await orchestrator.process_memory_candidate(
            content="Framework methodology for testing approaches",
            context={},
            existing_memories=existing,
        )

        assert decision["tier"] == MemoryTier.TIER1_PRINCIPLE
        assert decision["action"] == "queue_for_batch"
        assert decision["priority"] == "medium"

    @pytest.mark.asyncio
    async def test_full_decision_pipeline_tier2_high_score(self):
        """Complete pipeline: Solution + high importance → Batch queue"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content="Important bug fix: Correction needed for authentication flow",
            context={"corrects_previous_error": True},
            existing_memories=[],
        )

        assert decision["tier"] == MemoryTier.TIER2_SOLUTION
        assert decision["action"] == "queue_for_batch"
        assert decision["decay_function"] == DecayFunction.STALENESS_6MONTHS
        assert decision["priority"] == "medium"

    @pytest.mark.asyncio
    async def test_full_decision_pipeline_tier2_low_score(self):
        """Complete pipeline: Solution + low importance → Working memory"""
        orchestrator = AdaptiveMemoryOrchestrator()

        existing = ["Bug fix deployed", "Solution implemented"] * 3

        decision = await orchestrator.process_memory_candidate(
            content="Bug fix solution deployed successfully", context={}, existing_memories=existing
        )

        assert decision["tier"] == MemoryTier.TIER2_SOLUTION
        assert decision["action"] == "working_memory_only"
        assert decision["priority"] == "low"

    @pytest.mark.asyncio
    async def test_full_decision_pipeline_tier3_exceptional(self):
        """Complete pipeline: WIP + exceptional importance → Batch queue"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content=(
                "Working on important correction: "
                "actually unexpected validation result shows pattern break"
            ),
            context={
                "unexpected_result": True,
                "corrects_previous_error": True,
                "validation_result": "failed",
            },
            existing_memories=[],
        )

        assert decision["tier"] == MemoryTier.TIER3_CONTEXT
        assert decision["action"] == "queue_for_batch"
        assert decision["priority"] == "medium"

    @pytest.mark.asyncio
    async def test_full_decision_pipeline_tier3_normal(self):
        """Complete pipeline: WIP + normal importance → Working memory"""
        orchestrator = AdaptiveMemoryOrchestrator()

        decision = await orchestrator.process_memory_candidate(
            content="Working on CSS styling improvements",
            context={"is_temporary": True},
            existing_memories=[],
        )

        assert decision["tier"] == MemoryTier.TIER3_CONTEXT
        assert decision["action"] == "working_memory_only"
        assert decision["decay_function"] in [
            DecayFunction.RAPID_7DAYS,
            DecayFunction.RAPID_24HOURS,
        ]
        assert decision["priority"] == "low"


class TestComponentIntegration:
    """Gate 2: Integration Quality - Component Interactions"""

    @pytest.mark.asyncio
    async def test_command_parser_to_orchestrator_flow(self):
        """UserCommandParser detection triggers orchestrator override"""
        orchestrator = AdaptiveMemoryOrchestrator()

        test_commands = [
            "Remember this pattern",
            "Save this configuration",
            "Lesson learned about testing",
            "This is important information",
            "Always validate before deploy",
            "Never skip error handling",
        ]

        for command in test_commands:
            decision = await orchestrator.process_memory_candidate(
                content=command, context={}, existing_memories=None
            )

            assert (
                decision["action"] == "immediate_vectorize"
            ), f"Command should trigger immediate vectorize: {command}"
            assert (
                decision.get("user_commanded") is True
            ), f"Should mark as user commanded: {command}"

    @pytest.mark.asyncio
    async def test_evaluator_to_orchestrator_flow(self):
        """MemoryImportanceEvaluator scores influence orchestrator decisions"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # High score content (novel + emphasis + correction)
        high_score_decision = await orchestrator.process_memory_candidate(
            content="Important correction: actually the solution is different",
            context={"corrects_previous_error": True},
            existing_memories=[],
        )

        # Low score content (similar to existing)
        existing = ["Generic content about databases"] * 5
        low_score_decision = await orchestrator.process_memory_candidate(
            content="Generic content about databases", context={}, existing_memories=existing
        )

        # High score should lead to more aggressive actions
        assert high_score_decision["action"] in ["immediate_vectorize", "queue_for_batch"]
        # Similar content should be less aggressive
        assert low_score_decision["action"] in ["working_memory_only", "queue_for_batch"]

    @pytest.mark.asyncio
    async def test_classifier_to_orchestrator_flow(self):
        """H200TierClassifier tiers influence orchestrator thresholds"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # Same importance score, different tiers
        content = "New information discovered"  # Novel = 0.30

        # Tier 1 (threshold 0.6) - below threshold
        tier1_decision = await orchestrator.process_memory_candidate(
            content=f"Framework methodology: {content}", context={}, existing_memories=[]
        )

        # Tier 2 (threshold 0.7) - below threshold
        tier2_decision = await orchestrator.process_memory_candidate(
            content=f"Bug fix solution: {content}", context={}, existing_memories=[]
        )

        # Tier 3 (threshold 0.8) - below threshold
        tier3_decision = await orchestrator.process_memory_candidate(
            content=f"Working on: {content}", context={}, existing_memories=[]
        )

        # Different tiers should produce different actions for same score
        assert tier1_decision["action"] == "queue_for_batch"  # Tier 1: 0.30 < 0.6 → batch
        assert tier2_decision["action"] == "working_memory_only"  # Tier 2: 0.30 < 0.7 → working
        assert tier3_decision["action"] == "working_memory_only"  # Tier 3: 0.30 < 0.8 → working

    @pytest.mark.asyncio
    async def test_working_memory_buffer_integration(self):
        """Working memory buffer correctly stores and retrieves decisions"""
        orchestrator = AdaptiveMemoryOrchestrator()

        test_cases = [
            ("Framework principle for batch", {"is_framework_principle": True}),
            ("Working memory only content", {"is_temporary": True}),
            ("Another batch candidate", {"is_proven_solution": True}),
        ]

        for content, context in test_cases:
            decision = await orchestrator.process_memory_candidate(
                content=content, context=context, existing_memories=[]
            )
            orchestrator.add_to_working_memory(content, decision)

        # Verify buffer state
        assert len(orchestrator.memory_buffer) == 3
        for item in orchestrator.memory_buffer:
            assert "content" in item
            assert "decision" in item
            assert "timestamp" in item
            assert "hash" in item

        # Verify batch queue filtering
        batch_queue = orchestrator.get_batch_queue()
        batch_actions = [m["decision"]["action"] for m in batch_queue]
        assert all(action == "queue_for_batch" for action in batch_actions)

    @pytest.mark.asyncio
    async def test_context_propagation_through_pipeline(self):
        """Context flags propagate correctly through all components"""
        orchestrator = AdaptiveMemoryOrchestrator()

        context_flags = {
            "corrects_previous_error": True,
            "unexpected_result": True,
            "validation_result": "failed",
            "is_framework_principle": True,
        }

        decision = await orchestrator.process_memory_candidate(
            content="Test content with multiple context flags",
            context=context_flags,
            existing_memories=[],
        )

        # Context should influence both evaluator and classifier
        assert (
            "error" in decision["reasoning"].lower()
            or "correction" in decision["reasoning"].lower()
        )
        assert (
            "pattern break" in decision["reasoning"].lower()
            or "unexpected" in decision["reasoning"].lower()
        )
        assert decision["tier"] == MemoryTier.TIER1_PRINCIPLE

    @pytest.mark.asyncio
    async def test_existing_memories_influence_decisions(self):
        """Existing memories parameter influences importance scoring"""
        orchestrator = AdaptiveMemoryOrchestrator()

        content = "Framework methodology for testing validation"

        # No existing memories - should score higher (novel)
        decision_novel = await orchestrator.process_memory_candidate(
            content=content, context={}, existing_memories=[]
        )

        # Many similar existing memories - should score lower
        similar_existing = [
            "Framework methodology for testing",
            "Framework validation methodology",
            "Testing framework methodology",
        ] * 3

        decision_similar = await orchestrator.process_memory_candidate(
            content=content, context={}, existing_memories=similar_existing
        )

        # Novel content should get more aggressive action
        assert decision_novel["action"] in ["immediate_vectorize", "queue_for_batch"]
        # Similar content should be less aggressive
        assert decision_similar["action"] in ["queue_for_batch", "working_memory_only"]


class TestDecisionMatrixIntegration:
    """Gate 2: Integration Quality - Decision Matrix Completeness"""

    @pytest.mark.asyncio
    async def test_all_tier_action_combinations(self):
        """Test all valid tier × action combinations"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # Tier 0 → Always immediate_vectorize
        t0_decision = await orchestrator.process_memory_candidate(
            content="Never Fade to Black identity",
            context={"is_identity_anchor": True},
            existing_memories=None,
        )
        assert t0_decision["tier"] == MemoryTier.TIER0_ANCHOR
        assert t0_decision["action"] == "immediate_vectorize"

        # Tier 1 + high score → immediate_vectorize
        t1_high = await orchestrator.process_memory_candidate(
            content="Important framework principle: critical validation pattern",
            context={},
            existing_memories=[],
        )
        assert t1_high["tier"] == MemoryTier.TIER1_PRINCIPLE
        assert t1_high["action"] == "immediate_vectorize"

        # Tier 1 + low score → queue_for_batch
        t1_low = await orchestrator.process_memory_candidate(
            content="Framework methodology note",
            context={},
            existing_memories=["Framework methodology"] * 5,
        )
        assert t1_low["tier"] == MemoryTier.TIER1_PRINCIPLE
        assert t1_low["action"] == "queue_for_batch"

        # Tier 2 + high score → queue_for_batch
        t2_high = await orchestrator.process_memory_candidate(
            content="Important bug fix: correction for authentication flow",
            context={"corrects_previous_error": True},
            existing_memories=[],
        )
        assert t2_high["tier"] == MemoryTier.TIER2_SOLUTION
        assert t2_high["action"] == "queue_for_batch"

        # Tier 2 + low score → working_memory_only
        t2_low = await orchestrator.process_memory_candidate(
            content="Bug fix deployed", context={}, existing_memories=["Bug fix"] * 5
        )
        assert t2_low["tier"] == MemoryTier.TIER2_SOLUTION
        assert t2_low["action"] == "working_memory_only"

        # Tier 3 + exceptional score → queue_for_batch
        t3_high = await orchestrator.process_memory_candidate(
            content="Working on important correction with unexpected validation failure",
            context={
                "corrects_previous_error": True,
                "unexpected_result": True,
                "validation_result": "failed",
            },
            existing_memories=[],
        )
        assert t3_high["tier"] == MemoryTier.TIER3_CONTEXT
        assert t3_high["action"] == "queue_for_batch"

        # Tier 3 + low score → working_memory_only
        t3_low = await orchestrator.process_memory_candidate(
            content="Working on task", context={"is_temporary": True}, existing_memories=[]
        )
        assert t3_low["tier"] == MemoryTier.TIER3_CONTEXT
        assert t3_low["action"] == "working_memory_only"

    @pytest.mark.asyncio
    async def test_priority_levels_assigned_correctly(self):
        """Priority levels match tier and action combinations"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # Critical priority: Tier 0 or user commanded
        critical_t0 = await orchestrator.process_memory_candidate(
            content="Never Fade to Black",
            context={"is_identity_anchor": True},
            existing_memories=None,
        )
        assert critical_t0["priority"] == "critical"

        critical_cmd = await orchestrator.process_memory_candidate(
            content="Remember this pattern", context={}, existing_memories=None
        )
        assert critical_cmd["priority"] == "critical"

        # High priority: Tier 1 immediate vectorize
        high = await orchestrator.process_memory_candidate(
            content="Important framework methodology", context={}, existing_memories=[]
        )
        assert high["priority"] == "high"

        # Medium priority: Batch queue items
        medium = await orchestrator.process_memory_candidate(
            content="Framework principle", context={}, existing_memories=["framework"] * 5
        )
        assert medium["priority"] == "medium"

        # Low priority: Working memory only
        low = await orchestrator.process_memory_candidate(
            content="Working on task", context={"is_temporary": True}, existing_memories=[]
        )
        assert low["priority"] == "low"

    @pytest.mark.asyncio
    async def test_decay_functions_assigned_correctly(self):
        """Decay functions match memory tiers"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # Tier 0 → NEVER
        t0 = await orchestrator.process_memory_candidate(
            content="Never Fade to Black",
            context={"is_identity_anchor": True},
            existing_memories=None,
        )
        assert t0["decay_function"] == DecayFunction.NEVER

        # Tier 1 → SUPERSEDED_ONLY
        t1 = await orchestrator.process_memory_candidate(
            content="Framework methodology principle", context={}, existing_memories=[]
        )
        assert t1["decay_function"] == DecayFunction.SUPERSEDED_ONLY

        # Tier 2 → STALENESS_6MONTHS
        t2 = await orchestrator.process_memory_candidate(
            content="Bug fix solution deployed", context={}, existing_memories=[]
        )
        assert t2["decay_function"] == DecayFunction.STALENESS_6MONTHS

        # Tier 3 → RAPID (7 days or 24 hours)
        t3 = await orchestrator.process_memory_candidate(
            content="Working on task", context={"is_temporary": True}, existing_memories=[]
        )
        assert t3["decay_function"] in [DecayFunction.RAPID_7DAYS, DecayFunction.RAPID_24HOURS]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
