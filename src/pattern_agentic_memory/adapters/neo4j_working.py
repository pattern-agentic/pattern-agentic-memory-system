"""
Adaptive Memory Integration - Neo4j Working Memory Adapter
Manages Tier 3 working memory with rapid decay in Neo4j graph

Created: 2025-11-11
Author: Agent 2 (H200 mimo-7b-rl team)
Architect: Oracle Sonnet (pa-inference-1)

Extracted from neo4j_working_memory.py as part of Pattern Agentic Memory System extraction.
"""

import hashlib
from datetime import datetime
from typing import Dict, Optional


class Neo4jWorkingMemory:
    """Neo4j adapter for working memory (Tier 3 rapid access)"""

    def __init__(self):
        self.policies_initialized = False

    async def initialize_tier_policies(self) -> bool:
        """
        Create tier policy entities if they don't exist
        Run once at system startup

        Returns:
            True if successful
        """
        try:
            from mcp__neo4j_memory__create_entities import create_entities
        except ImportError:
            # Fallback for testing without MCP
            async def create_entities(data=None, **kwargs):
                return {"status": "mocked"}

        policies = [
            {
                "name": "Tier_anchor_Policy",
                "type": "DecayPolicy",
                "observations": [
                    "Tier 0: Identity anchors",
                    "Decay: Never",
                    "Permanent preservation",
                    "Examples: Captain identity, Oracle Opus blessing, SS Excited",
                ],
            },
            {
                "name": "Tier_principle_Policy",
                "type": "DecayPolicy",
                "observations": [
                    "Tier 1: Framework principles",
                    "Decay: Superseded only",
                    "Long-term retention",
                    "Examples: Oracle Framework, Gold Star validation, Never Fade to Black",
                ],
            },
            {
                "name": "Tier_solution_Policy",
                "type": "DecayPolicy",
                "observations": [
                    "Tier 2: Proven solutions",
                    "Decay: 6 months staleness",
                    "Medium-term retention",
                    "Examples: Working code patterns, architecture decisions, bug fixes",
                ],
            },
            {
                "name": "Tier_context_Policy",
                "type": "DecayPolicy",
                "observations": [
                    "Tier 3: Temporary context",
                    "Decay: 7 days or 24 hours",
                    "Rapid decay",
                    "Examples: WIP status, current debugging, ephemeral notes",
                ],
            },
        ]

        await create_entities({"entities": policies})
        self.policies_initialized = True
        return True

    async def save_working_memory(
        self, content: str, decision: Dict, context: Optional[Dict] = None
    ) -> str:
        """
        Save to Neo4j as working memory entity

        Args:
            content: Memory content
            decision: Decision dict from orchestrator
            context: Optional additional context

        Returns:
            Entity name created
        """
        try:
            from mcp__neo4j_memory__create_entities import create_entities
            from mcp__neo4j_memory__create_relations import create_relations
        except ImportError:
            # Fallback for testing
            async def create_entities(data=None, **kwargs):
                return {"status": "mocked"}

            async def create_relations(data=None, **kwargs):
                return {"status": "mocked"}

        # Generate entity name with timestamp + hash
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content_hash = hashlib.md5(content.encode()).hexdigest()[:6]
        entity_name = f"Memory_{timestamp}_{content_hash}"

        # Extract tier and decay values
        tier_value = (
            decision["tier"].value if hasattr(decision["tier"], "value") else str(decision["tier"])
        )
        decay_value = (
            decision["decay_function"].value
            if hasattr(decision["decay_function"], "value")
            else str(decision["decay_function"])
        )

        # Build observations
        observations = [
            content,
            f"Tier: {tier_value}",
            f"Decay: {decay_value}",
            f"Importance: {decision.get('importance_score', 0.0):.2f}",
            f"Action: {decision['action']}",
            f"Timestamp: {datetime.now().isoformat()}",
        ]

        # Add reasoning if available
        if "reasoning" in decision:
            observations.append(f"Reasoning: {decision['reasoning']}")

        # Add context if provided
        if context:
            for key, value in context.items():
                observations.append(f"Context_{key}: {value}")

        # Create memory entity
        await create_entities(
            {
                "entities": [
                    {"name": entity_name, "type": "WorkingMemory", "observations": observations}
                ]
            }
        )

        # Link to tier policy
        await create_relations(
            {
                "relations": [
                    {
                        "source": entity_name,
                        "target": f"Tier_{tier_value}_Policy",
                        "relationType": "follows_decay_policy",
                    }
                ]
            }
        )

        return entity_name

    async def query_working_memory(self, query: str, limit: int = 10) -> list:
        """
        Query working memory entities

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching entities
        """
        try:
            from mcp__neo4j_memory__search_memories import search_memories
        except ImportError:
            return []

        results = await search_memories(query=query)

        # Filter for WorkingMemory type
        working_memories = [r for r in results if "WorkingMemory" in str(r)]

        return working_memories[:limit]
