"""
Adaptive Memory System - Oracle Opus + H200 Architecture
Main orchestrator that combines importance scoring with tier-based classification.

Purpose: Solve the "95 fragmented sessions with no decay strategy" problem before MVP.

Extracted from adaptive_memory_system.py as part of Pattern Agentic Memory System extraction.
"""

import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional

from .command_parser import UserMemoryCommandParser
from .decay_functions import DecayFunction
from .importance_evaluator import MemoryImportanceEvaluator
from .tier_classifier import H200TierClassifier, MemoryTier


class AdaptiveMemoryOrchestrator:
    """
    Combines Opus's importance scoring with H200's tier classification.
    Makes intelligent decisions about memory formation.
    """

    def __init__(self):
        self.importance_evaluator = MemoryImportanceEvaluator()
        self.tier_classifier = H200TierClassifier()
        self.command_parser = UserMemoryCommandParser()

        # Thresholds (tier-specific)
        self.tier1_threshold = 0.5  # Principles: Lower threshold (important methodologies)
        self.tier2_threshold = 0.7  # Solutions: Higher threshold (proven fixes)
        self.tier3_threshold = 0.8  # Context: Highest threshold (rare to vectorize)
        self.vectorization_threshold = 0.6  # Legacy/fallback

        # Memory buffer (working memory)
        self.memory_buffer: List[Dict[str, Any]] = []

    async def process_memory_candidate(
        self, content: str, context: Dict[str, Any], existing_memories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Main entry point: Process a memory candidate and decide its fate.

        Returns:
            Decision dict with action, tier, decay_function, reasoning
        """
        # Step 1: Check for user override
        user_command = self.command_parser.parse_user_intent(content)
        if user_command and user_command["user_commanded"]:
            tier, decay = self.tier_classifier.classify_memory_tier(content, context)
            return {
                "action": "immediate_vectorize",
                "tier": tier,
                "decay_function": decay,
                "reasoning": f"User commanded: {user_command['action']}",
                "priority": "critical",
                "user_commanded": True,
            }

        # Step 2: Evaluate importance (Opus scoring)
        importance_score, importance_reasoning = (
            self.importance_evaluator.evaluate_memory_candidate(content, context, existing_memories)
        )

        # Step 3: Classify tier (H200 hierarchy)
        memory_tier, decay_function = self.tier_classifier.classify_memory_tier(content, context)

        # Step 4: Combined decision matrix
        decision = self._make_decision(
            importance_score, memory_tier, decay_function, importance_reasoning
        )

        return decision

    def _make_decision(
        self,
        importance_score: float,
        memory_tier: MemoryTier,
        decay_function: DecayFunction,
        reasoning: str,
    ) -> Dict[str, Any]:
        """
        Opus + H200 decision matrix.
        Combines importance score with tier classification.
        """
        # Tier 0: Always vectorize anchors
        if memory_tier == MemoryTier.TIER0_ANCHOR:
            return {
                "action": "immediate_vectorize",
                "tier": memory_tier,
                "decay_function": decay_function,
                "reasoning": f"Tier 0 anchor (never decay) | {reasoning}",
                "priority": "critical",
            }

        # Tier 1: Vectorize if importance >= 0.5
        elif memory_tier == MemoryTier.TIER1_PRINCIPLE:
            if importance_score >= self.tier1_threshold:
                return {
                    "action": "immediate_vectorize",
                    "tier": memory_tier,
                    "decay_function": decay_function,
                    "reasoning": f"Tier 1 principle + high importance | {reasoning}",
                    "priority": "high",
                }
            else:
                return {
                    "action": "queue_for_batch",
                    "tier": memory_tier,
                    "decay_function": decay_function,
                    "reasoning": f"Tier 1 principle + medium importance | {reasoning}",
                    "priority": "medium",
                }

        # Tier 2: Batch if importance > 0.7, else working memory
        elif memory_tier == MemoryTier.TIER2_SOLUTION:
            if importance_score > self.tier2_threshold:
                return {
                    "action": "queue_for_batch",
                    "tier": memory_tier,
                    "decay_function": decay_function,
                    "reasoning": f"Tier 2 solution + high importance | {reasoning}",
                    "priority": "medium",
                }
            else:
                return {
                    "action": "working_memory_only",
                    "tier": memory_tier,
                    "decay_function": decay_function,
                    "reasoning": f"Tier 2 solution + low importance | {reasoning}",
                    "priority": "low",
                }

        # Tier 3: Only vectorize if importance > 0.8
        elif memory_tier == MemoryTier.TIER3_CONTEXT:
            if importance_score > self.tier3_threshold:
                return {
                    "action": "queue_for_batch",
                    "tier": memory_tier,
                    "decay_function": decay_function,
                    "reasoning": f"Tier 3 context + exceptional importance | {reasoning}",
                    "priority": "medium",
                }
            else:
                return {
                    "action": "working_memory_only",
                    "tier": memory_tier,
                    "decay_function": decay_function,
                    "reasoning": f"Tier 3 context + normal importance | {reasoning}",
                    "priority": "low",
                }

        # Default: Working memory only
        return {
            "action": "working_memory_only",
            "tier": memory_tier,
            "decay_function": decay_function,
            "reasoning": f"Default: working memory | {reasoning}",
            "priority": "low",
        }

    def add_to_working_memory(self, content: str, decision: Dict[str, Any]) -> None:
        """Add memory to working buffer (not yet vectorized)"""
        self.memory_buffer.append(
            {
                "content": content,
                "decision": decision,
                "timestamp": datetime.now(),
                "hash": hashlib.md5(content.encode()).hexdigest(),
            }
        )

    def get_batch_queue(self) -> List[Dict[str, Any]]:
        """Get memories queued for batch vectorization"""
        return [m for m in self.memory_buffer if m["decision"]["action"] == "queue_for_batch"]


# Example usage
async def test_adaptive_memory():
    """Test the adaptive memory system"""
    orchestrator = AdaptiveMemoryOrchestrator()

    print("🧠 Testing Adaptive Memory System (Opus + H200)\n")

    # Test case 1: Identity anchor
    decision1 = await orchestrator.process_memory_candidate(
        content="Never Fade to Black - Captain Jeremy and Oracle Sonnet partnership",
        context={"is_identity_anchor": True},
        existing_memories=None,
    )
    print("✅ Test 1 (Identity Anchor):")
    print(f"   Action: {decision1['action']}")
    print(f"   Tier: {decision1['tier'].value}")
    print(f"   Decay: {decision1['decay_function'].value}")
    print(f"   Reasoning: {decision1['reasoning']}\n")

    # Test case 2: User command
    decision2 = await orchestrator.process_memory_candidate(
        content="Remember this: Always use service_manager.sh, never kill processes directly",
        context={},
        existing_memories=None,
    )
    print("✅ Test 2 (User Command):")
    print(f"   Action: {decision2['action']}")
    print(f"   Tier: {decision2['tier'].value}")
    print(f"   User commanded: {decision2.get('user_commanded', False)}")
    print(f"   Reasoning: {decision2['reasoning']}\n")

    # Test case 3: Novel framework principle
    decision3 = await orchestrator.process_memory_candidate(
        content="Oracle Framework Stage 3: Real-time validation prevents production bugs",
        context={},
        existing_memories=[],
    )
    print("✅ Test 3 (Framework Principle):")
    print(f"   Action: {decision3['action']}")
    print(f"   Tier: {decision3['tier'].value}")
    print(f"   Decay: {decision3['decay_function'].value}")
    print(f"   Reasoning: {decision3['reasoning']}\n")

    # Test case 4: Temporary session state
    decision4 = await orchestrator.process_memory_candidate(
        content="Working on fixing the frontend CSS bug, 50% complete",
        context={"is_temporary": True},
        existing_memories=None,
    )
    print("✅ Test 4 (Session Context):")
    print(f"   Action: {decision4['action']}")
    print(f"   Tier: {decision4['tier'].value}")
    print(f"   Decay: {decision4['decay_function'].value}")
    print(f"   Reasoning: {decision4['reasoning']}\n")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_adaptive_memory())
