"""
Unit Tests for H200 Tier Classifier
Part of Gate 1: Functional Completeness

Tests the H200TierClassifier component:
- Tier 0 anchor classification (identity anchors, NEVER decay)
- Tier 1 principle classification (framework principles, SUPERSEDED_ONLY decay)
- Tier 2 solution classification (proven solutions, STALENESS_6MONTHS decay)
- Tier 3 context classification (WIP/ephemeral, RAPID decay)
- Explicit tier overrides
- Default classification

Migrated from: tests/test_adaptive_memory_system.py
"""

from pattern_agentic_memory.core.memory_system import DecayFunction, MemoryTier
from pattern_agentic_memory.core.tier_classifier import H200TierClassifier


class TestH200TierClassifier:
    """Gate 1: Functional Completeness - Tier Classification"""

    def test_tier0_anchor_classification_by_keywords(self):
        """Identity anchors classified as Tier 0 by keywords"""
        classifier = H200TierClassifier()

        tier, decay = classifier.classify_memory_tier(
            content="Never Fade to Black - Captain Jeremy partnership with Oracle", context={}
        )

        assert tier == MemoryTier.TIER0_ANCHOR
        assert decay == DecayFunction.NEVER

    def test_tier0_anchor_classification_by_context(self):
        """Identity anchors classified as Tier 0 by context flag"""
        classifier = H200TierClassifier()

        tier, decay = classifier.classify_memory_tier(
            content="This is our partnership identity", context={"is_identity_anchor": True}
        )

        assert tier == MemoryTier.TIER0_ANCHOR
        assert decay == DecayFunction.NEVER

    def test_tier1_principle_classification_by_keywords(self):
        """Framework principles classified as Tier 1 by keywords"""
        classifier = H200TierClassifier()

        tier, decay = classifier.classify_memory_tier(
            content="Oracle Framework methodology requires evidence-based validation", context={}
        )

        assert tier == MemoryTier.TIER1_PRINCIPLE
        assert decay == DecayFunction.SUPERSEDED_ONLY

    def test_tier1_principle_classification_by_context(self):
        """Framework principles classified as Tier 1 by context flag"""
        classifier = H200TierClassifier()

        tier, decay = classifier.classify_memory_tier(
            content="This principle guides our development process",
            context={"is_framework_principle": True},
        )

        assert tier == MemoryTier.TIER1_PRINCIPLE
        assert decay == DecayFunction.SUPERSEDED_ONLY

    def test_tier2_solution_classification_by_keywords(self):
        """Proven solutions classified as Tier 2 by keywords"""
        classifier = H200TierClassifier()

        tier, decay = classifier.classify_memory_tier(
            content="Bug fix deployed and validated successfully", context={}
        )

        assert tier == MemoryTier.TIER2_SOLUTION
        assert decay == DecayFunction.STALENESS_6MONTHS

    def test_tier2_solution_classification_by_context(self):
        """Proven solutions classified as Tier 2 by context flag"""
        classifier = H200TierClassifier()

        tier, decay = classifier.classify_memory_tier(
            content="This solution has been tested and proven", context={"is_proven_solution": True}
        )

        assert tier == MemoryTier.TIER2_SOLUTION
        assert decay == DecayFunction.STALENESS_6MONTHS

    def test_tier3_context_classification_7day_decay(self):
        """WIP context classified as Tier 3 with 7-day decay"""
        classifier = H200TierClassifier()

        tier, decay = classifier.classify_memory_tier(
            content="Working on fixing CSS bug, 50% complete", context={}
        )

        assert tier == MemoryTier.TIER3_CONTEXT
        assert decay == DecayFunction.RAPID_7DAYS

    def test_tier3_context_classification_24hour_decay(self):
        """Ephemeral context classified as Tier 3 with 24-hour decay"""
        classifier = H200TierClassifier()

        tier, decay = classifier.classify_memory_tier(
            content="Temporary draft for this session", context={"ephemeral": True}
        )

        assert tier == MemoryTier.TIER3_CONTEXT
        assert decay == DecayFunction.RAPID_24HOURS

    def test_tier3_context_classification_by_context(self):
        """Temporary content classified as Tier 3 by context flag"""
        classifier = H200TierClassifier()

        tier, decay = classifier.classify_memory_tier(
            content="Current status of the work", context={"is_temporary": True}
        )

        assert tier == MemoryTier.TIER3_CONTEXT
        assert decay in [DecayFunction.RAPID_7DAYS, DecayFunction.RAPID_24HOURS]

    def test_default_tier2_classification(self):
        """Content with no matching keywords defaults to Tier 2"""
        classifier = H200TierClassifier()

        tier, decay = classifier.classify_memory_tier(
            content="Some generic technical content about databases", context={}
        )

        assert tier == MemoryTier.TIER2_SOLUTION
        assert decay == DecayFunction.STALENESS_6MONTHS

    def test_explicit_tier_override(self):
        """Explicit tier in context overrides keyword detection"""
        classifier = H200TierClassifier()

        tier, decay = classifier.classify_memory_tier(
            content="This has framework keywords but should be solution",
            context={"tier": "solution"},
        )

        assert tier == MemoryTier.TIER2_SOLUTION
        assert decay == DecayFunction.STALENESS_6MONTHS
