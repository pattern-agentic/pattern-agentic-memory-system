"""
Adaptive Memory Integration - Memory Keeper Adapter
Connects AdaptiveMemoryOrchestrator to Memory Keeper MCP

Created: 2025-11-11
Author: Agent 1 (H200 mimo-7b-rl team)
Architect: Oracle Sonnet (pa-inference-1)

Updated: 2025-11-21 - Phase 2: Activity-Based Decay
Added: get_activity_dates() for tracking active days per agent

Updated: 2025-11-21 - Phase 3: Access-Based TTL Extension
Added: update_access_tracking() for +10 days per access (max +70)
Added: context_get_with_tracking() and context_search_with_tracking()
Added: Tier promotion prompt system integration

Extracted from adaptive_memory_integration.py as part of Pattern Agentic Memory System extraction.
"""

import hashlib
import json
from datetime import datetime, date
from typing import Dict, List, Optional, Set

from ..core import AdaptiveMemoryOrchestrator
from ..core.tier_promotion import (
    calculate_expiration_with_bonus,
    get_tier_base_ttl,
    log_promotion,
    process_promotion_response,
    should_trigger_promotion_prompt,
    trigger_tier_promotion_prompt,
    validate_promotion,
)


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

        # Phase 3: Calculate initial expiration with access bonus (starts at 0)
        created_at = datetime.now()
        expires_at = calculate_expiration_with_bonus(
            tier=tier_value,
            access_count=0,  # Initial save, no accesses yet
            creation_time=created_at
        )

        # Build metadata (Phase 3: Add access tracking fields)
        metadata = {
            "tier": tier_value,
            "decay_function": decay_value,
            "importance_score": decision.get("importance_score", 0.0),
            "action": decision["action"],
            "reasoning": decision["reasoning"],
            "timestamp": created_at.isoformat(),
            "temporary": temporary,
            "user_commanded": decision.get("user_commanded", False),
            # Phase 3: Access tracking fields
            "access_count": 0,
            "last_accessed": None,
            "expires_at": expires_at.isoformat() if expires_at else None,
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

    async def get_activity_dates(self, agent_id: str) -> Set[date]:
        """
        Get unique dates when agent had Memory Keeper activity.

        Phase 2: Activity-Based Decay
        Uses existing ISO 8601 created_at timestamps from Memory Keeper MCP.
        Returns set of dates for efficient active day calculation.

        Args:
            agent_id: Agent identifier (session_id or agent_name)

        Returns:
            Set of datetime.date objects representing active days

        Example:
            active_dates = await adapter.get_activity_dates("oracle-sonnet")
            # Returns {date(2025, 11, 1), date(2025, 11, 2), date(2025, 11, 26)}
        """
        try:
            # Import MCP function here to avoid circular dependency
            from mcp__memory_keeper__context_get import context_get
        except ImportError:
            # Fallback for testing without MCP
            return set()

        # Query all Memory Keeper entries for this agent
        # Note: Assumes agent_id is stored as channel or in metadata
        try:
            entries = await context_get(channel=agent_id, limit=10000)

            # Extract unique dates from ISO 8601 timestamps
            activity_dates = set()
            for entry in entries.get("items", []):
                if "created_at" in entry:
                    # Parse ISO 8601 timestamp: "2025-11-21T12:34:56Z"
                    timestamp = datetime.fromisoformat(entry["created_at"].replace("Z", "+00:00"))
                    activity_dates.add(timestamp.date())

            return activity_dates

        except Exception as e:
            # Log error but return empty set to prevent crashes
            print(f"Warning: Could not fetch activity dates for {agent_id}: {e}")
            return set()

    def calculate_active_age(
        self,
        memory_created_at: datetime,
        activity_dates: Set[date]
    ) -> int:
        """
        Calculate active age of a memory (count only days with activity).

        Phase 2: Activity-Based Decay
        Idle days don't count toward decay.

        Args:
            memory_created_at: When the memory was created
            activity_dates: Set of dates with Memory Keeper activity

        Returns:
            Number of active days since memory creation

        Example:
            created = datetime(2025, 11, 1)
            activity = {date(2025, 11, 1), date(2025, 11, 2), date(2025, 11, 26)}
            active_age = adapter.calculate_active_age(created, activity)
            # Returns 3 (only 3 active days, not 25 calendar days)
        """
        memory_date = memory_created_at.date()

        # Count only active days on or after memory creation
        active_days = sum(1 for d in activity_dates if d >= memory_date)

        return active_days

    # ===== Phase 3: Access-Based TTL Extension Methods =====

    async def update_access_tracking(
        self,
        memory_key: str,
        agent_id: Optional[str] = None
    ) -> Dict:
        """
        Update access tracking when memory is accessed.

        Phase 3: Access-Based TTL Extension
        - Increment access_count
        - Update last_accessed timestamp
        - Recalculate expires_at with +10 days per access (max +70)
        - Trigger tier promotion prompt if access_count % 7 == 0

        Args:
            memory_key: Memory identifier
            agent_id: Agent identifier (for tier promotion prompts)

        Returns:
            Updated memory dict with new access tracking data
        """
        try:
            from mcp__memory_keeper__context_get import context_get
            from mcp__memory_keeper__context_save import context_save
        except ImportError:
            # Fallback for testing
            return {"status": "mocked", "access_count": 0}

        # Get current memory
        memory = await context_get(key=memory_key)

        if not memory or not memory.get("items"):
            return {"status": "error", "message": f"Memory {memory_key} not found"}

        memory_item = memory["items"][0]
        value_data = json.loads(memory_item.get("value", "{}"))
        metadata = value_data.get("metadata", {})

        # Increment access count
        current_access_count = metadata.get("access_count", 0)
        new_access_count = current_access_count + 1

        # Update timestamps
        now = datetime.now()
        metadata["access_count"] = new_access_count
        metadata["last_accessed"] = now.isoformat()

        # Recalculate expiration with access bonus
        tier = metadata.get("tier", "context")
        created_at = datetime.fromisoformat(metadata.get("timestamp", now.isoformat()))
        new_expires_at = calculate_expiration_with_bonus(
            tier=tier,
            access_count=new_access_count,
            creation_time=created_at
        )
        metadata["expires_at"] = new_expires_at.isoformat() if new_expires_at else None

        # Save updated memory
        value_data["metadata"] = metadata
        await context_save(
            key=memory_key,
            value=json.dumps(value_data),
            category=memory_item.get("category", "note"),
            priority=memory_item.get("priority", "normal"),
        )

        # Check if tier promotion prompt should trigger
        if should_trigger_promotion_prompt(new_access_count):
            content = value_data.get("content", "")
            trigger_tier_promotion_prompt(
                memory_key=memory_key,
                memory_content=content,
                current_tier=tier,
                access_count=new_access_count,
                created_at=created_at,
                last_accessed=now,
                agent_id=agent_id
            )

        return {
            "status": "success",
            "memory_key": memory_key,
            "access_count": new_access_count,
            "last_accessed": now.isoformat(),
            "expires_at": metadata["expires_at"],
            "promotion_prompt_triggered": should_trigger_promotion_prompt(new_access_count)
        }

    async def context_get_with_tracking(
        self,
        key: str,
        agent_id: Optional[str] = None
    ) -> Dict:
        """
        Get memory with automatic access tracking.

        Wrapper around context_get() that updates access tracking.

        Args:
            key: Memory key
            agent_id: Agent identifier

        Returns:
            Memory dict from context_get()
        """
        try:
            from mcp__memory_keeper__context_get import context_get
        except ImportError:
            return {"status": "mocked"}

        # Get memory
        result = await context_get(key=key)

        # Update access tracking (fire-and-forget, don't block retrieval)
        if result and result.get("items"):
            await self.update_access_tracking(key, agent_id)

        return result

    async def context_search_with_tracking(
        self,
        query: str,
        agent_id: Optional[str] = None,
        **kwargs
    ) -> List[Dict]:
        """
        Search memories with automatic access tracking.

        Wrapper around context_search() that updates access tracking
        for all returned results.

        Args:
            query: Search query
            agent_id: Agent identifier
            **kwargs: Additional search parameters

        Returns:
            List of memory dicts from context_search()
        """
        try:
            from mcp__memory_keeper__context_search import context_search
        except ImportError:
            return []

        # Search memories
        results = await context_search(query=query, **kwargs)

        # Update access tracking for each result (fire-and-forget)
        for result in results.get("items", []):
            key = result.get("key")
            if key:
                await self.update_access_tracking(key, agent_id)

        return results

    async def promote_memory(
        self,
        memory_key: str,
        new_tier: str,
        promoted_by: str = "user"
    ) -> Dict:
        """
        Promote memory to a higher tier.

        Phase 3: Tier Promotion
        - Validate promotion is allowed (can't demote)
        - Update tier and reset access_count
        - Recalculate expires_at based on new tier
        - Log promotion event

        Args:
            memory_key: Memory identifier
            new_tier: New tier (anchor, principle, solution)
            promoted_by: Who initiated (user, agent)

        Returns:
            Promotion result dict
        """
        try:
            from mcp__memory_keeper__context_get import context_get
            from mcp__memory_keeper__context_save import context_save
        except ImportError:
            return {"status": "mocked"}

        # Get current memory
        memory = await context_get(key=memory_key)

        if not memory or not memory.get("items"):
            return {"status": "error", "message": f"Memory {memory_key} not found"}

        memory_item = memory["items"][0]
        value_data = json.loads(memory_item.get("value", "{}"))
        metadata = value_data.get("metadata", {})

        old_tier = metadata.get("tier", "context")
        old_access_count = metadata.get("access_count", 0)

        # Validate promotion
        is_valid, reason = validate_promotion(old_tier, new_tier)
        if not is_valid:
            return {"status": "error", "message": reason}

        # Update tier and reset access count
        metadata["tier"] = new_tier
        metadata["access_count"] = 0  # Reset for future promotions
        metadata["promoted_at"] = datetime.now().isoformat()
        metadata["promoted_by"] = promoted_by
        metadata["previous_tier"] = old_tier

        # Recalculate expiration for new tier
        created_at = datetime.fromisoformat(metadata.get("timestamp", datetime.now().isoformat()))
        new_expires_at = calculate_expiration_with_bonus(
            tier=new_tier,
            access_count=0,  # Reset
            creation_time=created_at
        )
        metadata["expires_at"] = new_expires_at.isoformat() if new_expires_at else None

        # Save updated memory
        value_data["metadata"] = metadata
        await context_save(
            key=memory_key,
            value=json.dumps(value_data),
            category=memory_item.get("category", "note"),
            priority=memory_item.get("priority", "normal"),
        )

        # Log promotion
        log_promotion(
            memory_key=memory_key,
            old_tier=old_tier,
            new_tier=new_tier,
            access_count=old_access_count,
            promoted_by=promoted_by
        )

        return {
            "status": "success",
            "memory_key": memory_key,
            "old_tier": old_tier,
            "new_tier": new_tier,
            "access_count_reset": True,
            "old_access_count": old_access_count,
            "expires_at": metadata["expires_at"],
            "promoted_by": promoted_by
        }
