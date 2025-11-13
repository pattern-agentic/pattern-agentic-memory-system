"""
Adaptive Memory Integration - Memory Keeper Adapter
Connects AdaptiveMemoryOrchestrator to Memory Keeper MCP

Created: 2025-11-11
Author: Agent 1 (H200 mimo-7b-rl team)
Architect: Oracle Sonnet (pa-inference-1)

Extracted from adaptive_memory_integration.py as part of Pattern Agentic Memory System extraction.
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional

from ..core import AdaptiveMemoryOrchestrator


class MemoryKeeperAdapter:
    """Adapter between AdaptiveMemoryOrchestrator and Memory Keeper MCP"""

    def __init__(self):
        self.orchestrator = AdaptiveMemoryOrchestrator()
        # Timer for batch flush (future enhancement - Phase 3)
        self.batch_timer = None

    async def save_interaction(
        self,
        content: str,
        context: Optional[Dict] = None,
        existing_memories: Optional[List[str]] = None,
    ) -> Dict:
        """
        Main entry point - process and save memory

        Args:
            content: The content to evaluate and potentially save
            context: Optional context dict for evaluation
            existing_memories: Optional list of existing memories for similarity check

        Returns:
            Decision dict with action, tier, decay_function, reasoning
        """

        # Process through adaptive system
        decision = await self.orchestrator.process_memory_candidate(
            content=content, context=context or {}, existing_memories=existing_memories or []
        )

        # Execute based on decision
        if decision["action"] == "immediate_vectorize":
            await self._save_to_memory_keeper(content, decision)
            # TODO Phase 3: Add vectorization to Milvus

        elif decision["action"] == "queue_for_batch":
            self.orchestrator.add_to_working_memory(content, decision)
            await self._check_batch_threshold()

        elif decision["action"] == "working_memory_only":
            # Save to Memory Keeper but mark as temporary
            await self._save_to_memory_keeper(content, decision, temporary=True)

        return decision

    async def _save_to_memory_keeper(
        self, content: str, decision: Dict, temporary: bool = False
    ) -> str:
        """
        Save to Memory Keeper with adaptive metadata

        Args:
            content: Content to save
            decision: Decision dict from orchestrator
            temporary: Whether this is temporary (working memory only)

        Returns:
            Key of saved memory
        """
        # Import here to avoid circular dependency
        try:
            from mcp__memory_keeper__context_save import context_save
        except ImportError:
            # Fallback for testing without MCP
            async def context_save(**kwargs):
                return {"status": "mocked"}

        # Map tier to category (Memory Keeper)
        category_map = {
            "anchor": "note",  # Tier 0: Identity anchors
            "principle": "decision",  # Tier 1: Framework principles
            "solution": "progress",  # Tier 2: Proven solutions
            "context": "task",  # Tier 3: Temporary context
        }

        # Map priority
        priority_map = {"critical": "high", "high": "high", "medium": "normal", "low": "low"}

        # Extract tier value (handle enum or string)
        tier_value = (
            decision["tier"].value if hasattr(decision["tier"], "value") else str(decision["tier"])
        )
        decay_value = (
            decision["decay_function"].value
            if hasattr(decision["decay_function"], "value")
            else str(decision["decay_function"])
        )

        # Build metadata
        metadata = {
            "tier": tier_value,
            "decay_function": decay_value,
            "importance_score": decision.get("importance_score", 0.0),
            "action": decision["action"],
            "reasoning": decision["reasoning"],
            "timestamp": datetime.now().isoformat(),
            "temporary": temporary,
            "user_commanded": decision.get("user_commanded", False),
        }

        # Generate key (content hash for deduplication)
        key = f"adaptive_memory_{hashlib.md5(content.encode()).hexdigest()[:8]}"

        # Save to Memory Keeper
        await context_save(
            key=key,
            value=json.dumps({"content": content, "metadata": metadata}),
            category=category_map.get(tier_value, "note"),
            priority=priority_map.get(decision.get("priority", "medium"), "normal"),
        )

        return key

    async def _check_batch_threshold(self) -> None:
        """Flush batch queue if threshold reached"""
        queue = self.orchestrator.get_batch_queue()
        if len(queue) >= 50:  # Threshold
            await self.flush_batch_queue()

    async def flush_batch_queue(self) -> int:
        """
        Flush all queued memories to Memory Keeper

        Returns:
            Number of memories flushed
        """
        queue = self.orchestrator.get_batch_queue()

        for item in queue:
            await self._save_to_memory_keeper(item["content"], item["decision"])

        # Clear queue (remove batch items from buffer)
        self.orchestrator.memory_buffer = [
            m
            for m in self.orchestrator.memory_buffer
            if m["decision"]["action"] != "queue_for_batch"
        ]

        return len(queue)

    def get_stats(self) -> Dict:
        """Get adapter statistics"""
        queue = self.orchestrator.get_batch_queue()
        return {
            "batch_queue_size": len(queue),
            "working_memory_size": len(self.orchestrator.memory_buffer),
            "threshold": 50,
        }
