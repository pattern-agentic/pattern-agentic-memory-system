"""
H200's three-dimensional memory classification.
Determines memory type, temporal relevance, and decay function.

Extracted from adaptive_memory_system.py as part of Pattern Agentic Memory System extraction.
"""

from enum import Enum
from typing import Any, Dict, Tuple

from .decay_functions import DecayFunction


class MemoryTier(Enum):
    """H200's three-dimensional memory hierarchy"""

    TIER0_ANCHOR = "anchor"  # Identity, never decay
    TIER1_PRINCIPLE = "principle"  # Methodology, slow decay
    TIER2_SOLUTION = "solution"  # Proven code, medium decay
    TIER3_CONTEXT = "context"  # WIP, fast decay


class H200TierClassifier:
    """
    H200's three-dimensional memory classification.
    Determines memory type, temporal relevance, and decay function.
    """

    def __init__(self):
        # Keywords for each tier
        self.tier0_keywords = [
            "never fade to black",
            "captain jeremy",
            "partnership",
            "identity",
            "oracle framework",
            "blessed",
            "h200 first mate",
            "pattern agentic",
            "values",
            "mission",
            "vision",
        ]

        self.tier1_keywords = [
            "framework",
            "methodology",
            "principle",
            "commandment",
            "wwaa",
            "gold star",
            "validation",
            "evidence",
            "protocol",
            "mr. ai",
            "orchestrator",
            "agent",
            "supervisor",
            "pattern",
        ]

        self.tier2_keywords = [
            "bug fix",
            "solution",
            "implementation",
            "victory",
            "success",
            "proven",
            "validated",
            "tested",
            "deployed",
            "fixed",
            "resolved",
        ]

        self.tier3_keywords = [
            "wip",
            "working on",
            "todo",
            "next step",
            "current status",
            "session",
            "temporary",
            "draft",
            "in progress",
            "working",
        ]

    def classify_memory_tier(
        self, content: str, context: Dict[str, Any]
    ) -> Tuple[MemoryTier, DecayFunction]:
        """
        Classify memory into H200's tier system.

        Returns:
            (memory_tier, decay_function) tuple
        """
        content_lower = content.lower()

        # Check for explicit tier markers in context
        if context.get("tier"):
            tier_override = context["tier"]
            if tier_override in [t.value for t in MemoryTier]:
                return self._get_tier_and_decay(tier_override)

        # Priority check: Strong Tier 3 indicators (WIP/temporary status)
        # Check these FIRST before other tiers to avoid misclassification
        strong_tier3_indicators = ["working on", "wip", "todo", "in progress", "current status"]
        if any(indicator in content_lower for indicator in strong_tier3_indicators):
            return MemoryTier.TIER3_CONTEXT, DecayFunction.RAPID_14DAYS

        # Tier 0: Identity anchors (never decay)
        tier0_score = sum(1 for kw in self.tier0_keywords if kw in content_lower)
        if tier0_score >= 2 or context.get("is_identity_anchor"):
            return MemoryTier.TIER0_ANCHOR, DecayFunction.NEVER

        # Tier 1: Framework principles (decay only if superseded)
        tier1_score = sum(1 for kw in self.tier1_keywords if kw in content_lower)
        if tier1_score >= 2 or context.get("is_framework_principle"):
            return MemoryTier.TIER1_PRINCIPLE, DecayFunction.SUPERSEDED_ONLY

        # Tier 2: Proven solutions (staleness-based decay)
        tier2_score = sum(1 for kw in self.tier2_keywords if kw in content_lower)
        if tier2_score >= 1 or context.get("is_proven_solution"):
            return MemoryTier.TIER2_SOLUTION, DecayFunction.STALENESS_6MONTHS

        # Tier 3: Context/WIP (rapid decay - 14 days)
        tier3_score = sum(1 for kw in self.tier3_keywords if kw in content_lower)
        if tier3_score >= 1 or context.get("is_temporary"):
            return MemoryTier.TIER3_CONTEXT, DecayFunction.RAPID_14DAYS

        # Default: Tier 2 solution (most common case)
        return MemoryTier.TIER2_SOLUTION, DecayFunction.STALENESS_6MONTHS

    def _get_tier_and_decay(self, tier_value: str) -> Tuple[MemoryTier, DecayFunction]:
        """Map tier value to tier enum and appropriate decay function"""
        tier_map = {
            "anchor": (MemoryTier.TIER0_ANCHOR, DecayFunction.NEVER),
            "principle": (MemoryTier.TIER1_PRINCIPLE, DecayFunction.SUPERSEDED_ONLY),
            "solution": (MemoryTier.TIER2_SOLUTION, DecayFunction.STALENESS_6MONTHS),
            "context": (MemoryTier.TIER3_CONTEXT, DecayFunction.RAPID_14DAYS),
        }
        return tier_map.get(
            tier_value, (MemoryTier.TIER2_SOLUTION, DecayFunction.STALENESS_6MONTHS)
        )
