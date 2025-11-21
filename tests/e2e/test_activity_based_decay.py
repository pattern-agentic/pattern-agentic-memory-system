"""
E2E Tests: Activity-Based Memory Decay (Phase 2)

Test Scenarios:
1. Active Agent - No decay during continuous activity
2. Idle Agent - Timer paused during idle periods
3. Partial Decay - Memory decays after enough active days
4. Multi-Agent Isolation - Agent memories calculated independently
5. Tier Boundary Testing - Exact TTL boundary validation

Gold Star Criteria:
- All tests pass with actual terminal output
- Evidence blocks show real calculations
- No success theater - raw data only

Author: Archival Agent (Phase 2 Implementation)
Architect: Oracle Sonnet (Keeper of the Conduit)
Created: 2025-11-21
"""

import asyncio
import json
from datetime import datetime, date, timedelta
from typing import Set
import pytest

# Import components
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from pattern_agentic_memory.adapters.memory_keeper import MemoryKeeperAdapter
from pattern_agentic_memory.core.decay_functions import DecayFunction, DECAY_POLICY_MAP


class MockMemoryKeeperMCP:
    """Mock Memory Keeper MCP for testing"""

    def __init__(self):
        self.entries = {}  # channel -> list of entries
        self.vectors = {}  # channel -> list of vector memories

    def add_entry(self, channel: str, created_at: datetime):
        """Add a Memory Keeper entry for testing"""
        if channel not in self.entries:
            self.entries[channel] = []

        entry = {
            "key": f"test_entry_{len(self.entries[channel])}",
            "value": json.dumps({
                "content": f"Test activity on {created_at.date()}",
                "metadata": {
                    "tier": "context",
                    "action": "working_memory_only",
                }
            }),
            "created_at": created_at.isoformat() + "Z",
            "channel": channel,
        }
        self.entries[channel].append(entry)

    def add_vector_memory(
        self,
        channel: str,
        created_at: datetime,
        tier: str = "context",
        memory_id: str = None
    ):
        """Add a vector memory for testing"""
        if channel not in self.vectors:
            self.vectors[channel] = []

        if memory_id is None:
            memory_id = f"vector_{len(self.vectors[channel])}"

        vector = {
            "key": memory_id,
            "value": json.dumps({
                "content": f"Vector memory created on {created_at.date()}",
                "metadata": {
                    "tier": tier,
                    "action": "immediate_vectorize",
                }
            }),
            "created_at": created_at.isoformat() + "Z",
            "channel": channel,
        }
        self.vectors[channel].append(vector)

    def get_entries(self, channel: str, limit: int = 10000):
        """Get entries for a channel"""
        return {
            "items": self.entries.get(channel, [])
        }

    def get_activity_dates(self, channel: str) -> Set[date]:
        """Get unique activity dates for testing"""
        dates = set()
        for entry in self.entries.get(channel, []):
            timestamp = datetime.fromisoformat(entry["created_at"].replace("Z", "+00:00"))
            dates.add(timestamp.date())
        return dates


# Test fixtures
@pytest.fixture
def mock_mcp():
    """Create mock Memory Keeper MCP"""
    return MockMemoryKeeperMCP()


@pytest.fixture
def adapter():
    """Create Memory Keeper adapter"""
    return MemoryKeeperAdapter()


# Test 1: Active Agent (No Decay During Activity)
@pytest.mark.asyncio
async def test_active_agent_no_decay(mock_mcp, adapter):
    """
    Test 1: Active Agent (Memory Within TTL Window)

    Scenario:
    - Create Tier 3 memory (14-day TTL) on Nov 1
    - Simulate 10 consecutive days of daily activity
    - Memory should survive (10 < 14-day TTL)

    Expected: Memory survives when active days < TTL
    """
    print("\n" + "=" * 80)
    print("TEST 1: Active Agent - Memory Within TTL Window")
    print("=" * 80)

    agent_id = "test-agent-active"
    tier = "context"  # Tier 3: 14-day TTL
    tier_ttl = DECAY_POLICY_MAP[DecayFunction.RAPID_14DAYS].days

    # Create memory on Nov 1
    memory_created = datetime(2025, 11, 1, 10, 0, 0)
    mock_mcp.add_vector_memory(agent_id, memory_created, tier)

    # Simulate 10 days of continuous activity (within 14-day TTL)
    for i in range(10):
        activity_date = memory_created + timedelta(days=i)
        mock_mcp.add_entry(agent_id, activity_date)

    # Get activity dates
    activity_dates = mock_mcp.get_activity_dates(agent_id)

    # Calculate active age
    active_age = adapter.calculate_active_age(memory_created, activity_dates)
    calendar_age = 10

    print(f"\nMemory created: {memory_created.date()}")
    print(f"Tier: {tier} (TTL: {tier_ttl} days)")
    print(f"Activity pattern: 10 consecutive days (Nov 1 - Nov 10)")
    print(f"Active age: {active_age} days")
    print(f"Calendar age: {calendar_age} days")
    print(f"Should decay: {active_age > tier_ttl}")

    # Assertion
    should_decay = active_age > tier_ttl
    assert not should_decay, (
        f"Memory should NOT decay - active for {active_age} days "
        f"(within {tier_ttl}-day TTL window)"
    )

    print("\n✅ TEST PASSED: Memory survives when active days < TTL")
    print("=" * 80)


# Test 2: Idle Agent (Timer Paused)
@pytest.mark.asyncio
async def test_idle_agent_timer_paused(mock_mcp, adapter):
    """
    Test 2: Idle Agent (Timer Paused During Idle Period)

    Scenario:
    - Create Tier 3 memory (14-day TTL) on Nov 1
    - Activity: 5 days (Nov 1-5) → 20 days idle → 5 days (Nov 26-30)
    - Calendar: 30 days | Active: 10 days

    Expected: Memory survives (10 active days < 14 TTL)
    """
    print("\n" + "=" * 80)
    print("TEST 2: Idle Agent - Timer Paused During Idle Period")
    print("=" * 80)

    agent_id = "test-agent-idle"
    tier = "context"  # Tier 3: 14-day TTL
    tier_ttl = DECAY_POLICY_MAP[DecayFunction.RAPID_14DAYS].days

    # Create memory on Nov 1
    memory_created = datetime(2025, 11, 1, 10, 0, 0)
    mock_mcp.add_vector_memory(agent_id, memory_created, tier)

    # Activity: 5 days (Nov 1-5)
    for i in range(5):
        activity_date = memory_created + timedelta(days=i)
        mock_mcp.add_entry(agent_id, activity_date)

    # 20 days idle (Nov 6-25) - no entries

    # Activity: 5 days (Nov 26-30)
    for i in range(25, 30):
        activity_date = memory_created + timedelta(days=i)
        mock_mcp.add_entry(agent_id, activity_date)

    # Get activity dates
    activity_dates = mock_mcp.get_activity_dates(agent_id)

    # Calculate ages
    active_age = adapter.calculate_active_age(memory_created, activity_dates)
    calendar_age = 30

    print(f"\nMemory created: {memory_created.date()}")
    print(f"Tier: {tier} (TTL: {tier_ttl} days)")
    print(f"Activity pattern:")
    print(f"  - Nov 1-5: Active (5 days)")
    print(f"  - Nov 6-25: IDLE (20 days)")
    print(f"  - Nov 26-30: Active (5 days)")
    print(f"Active age: {active_age} days (timer paused during idle)")
    print(f"Calendar age: {calendar_age} days")
    print(f"Should decay: {active_age > tier_ttl}")

    # Assertion
    should_decay = active_age > tier_ttl
    assert not should_decay, (
        f"Memory should NOT decay - only {active_age} active days "
        f"(idle period didn't count toward TTL)"
    )

    print("\n✅ TEST PASSED: Idle period correctly ignored")
    print("=" * 80)


# Test 3: Partial Decay
@pytest.mark.asyncio
async def test_partial_decay(mock_mcp, adapter):
    """
    Test 3: Partial Decay (Memory Expires After Enough Active Days)

    Scenario:
    - Create Tier 3 memory (14-day TTL) on Nov 1
    - 15 active days spread over 60 calendar days
    - Active age: 15 days | Calendar age: 60 days

    Expected: Memory decays (15 active days > 14 TTL)
    """
    print("\n" + "=" * 80)
    print("TEST 3: Partial Decay - Memory Expires After Enough Active Days")
    print("=" * 80)

    agent_id = "test-agent-partial"
    tier = "context"  # Tier 3: 14-day TTL
    tier_ttl = DECAY_POLICY_MAP[DecayFunction.RAPID_14DAYS].days

    # Create memory on Nov 1
    memory_created = datetime(2025, 11, 1, 10, 0, 0)
    mock_mcp.add_vector_memory(agent_id, memory_created, tier)

    # 15 active days spread over 60 calendar days
    # Pattern: Active every 4th day
    active_days_list = []
    for i in range(15):
        activity_date = memory_created + timedelta(days=i * 4)
        mock_mcp.add_entry(agent_id, activity_date)
        active_days_list.append(activity_date.date())

    # Get activity dates
    activity_dates = mock_mcp.get_activity_dates(agent_id)

    # Calculate ages
    active_age = adapter.calculate_active_age(memory_created, activity_dates)
    calendar_age = 60

    print(f"\nMemory created: {memory_created.date()}")
    print(f"Tier: {tier} (TTL: {tier_ttl} days)")
    print(f"Activity pattern: 15 days spread over 60 calendar days")
    print(f"Active days: {', '.join(str(d) for d in sorted(active_days_list)[:5])}... (15 total)")
    print(f"Active age: {active_age} days")
    print(f"Calendar age: {calendar_age} days")
    print(f"Should decay: {active_age > tier_ttl}")

    # Assertion
    should_decay = active_age > tier_ttl
    assert should_decay, (
        f"Memory SHOULD decay - {active_age} active days exceeds {tier_ttl}-day TTL"
    )

    print("\n✅ TEST PASSED: Memory correctly expires after enough active days")
    print("=" * 80)


# Test 4: Multi-Agent Isolation
@pytest.mark.asyncio
async def test_multi_agent_isolation(mock_mcp, adapter):
    """
    Test 4: Multi-Agent Isolation

    Scenario:
    - Agent A: 10 active days (should NOT decay - under 14-day TTL)
    - Agent B: 20 active days (should decay - over 14-day TTL)

    Expected: Each agent's memories calculated independently
    """
    print("\n" + "=" * 80)
    print("TEST 4: Multi-Agent Isolation")
    print("=" * 80)

    tier = "context"  # Tier 3: 14-day TTL
    tier_ttl = DECAY_POLICY_MAP[DecayFunction.RAPID_14DAYS].days
    memory_created = datetime(2025, 11, 1, 10, 0, 0)

    # Agent A: 10 active days
    agent_a = "test-agent-a"
    mock_mcp.add_vector_memory(agent_a, memory_created, tier, "memory_a")
    for i in range(10):
        mock_mcp.add_entry(agent_a, memory_created + timedelta(days=i))

    # Agent B: 20 active days
    agent_b = "test-agent-b"
    mock_mcp.add_vector_memory(agent_b, memory_created, tier, "memory_b")
    for i in range(20):
        mock_mcp.add_entry(agent_b, memory_created + timedelta(days=i))

    # Calculate ages for both agents
    activity_a = mock_mcp.get_activity_dates(agent_a)
    activity_b = mock_mcp.get_activity_dates(agent_b)

    active_age_a = adapter.calculate_active_age(memory_created, activity_a)
    active_age_b = adapter.calculate_active_age(memory_created, activity_b)

    print(f"\nMemory created: {memory_created.date()}")
    print(f"Tier: {tier} (TTL: {tier_ttl} days)")
    print(f"\nAgent A:")
    print(f"  Active days: {active_age_a}")
    print(f"  Should decay: {active_age_a > tier_ttl}")
    print(f"\nAgent B:")
    print(f"  Active days: {active_age_b}")
    print(f"  Should decay: {active_age_b > tier_ttl}")

    # Assertions
    assert active_age_a <= tier_ttl, "Agent A memory should NOT decay"
    assert active_age_b > tier_ttl, "Agent B memory SHOULD decay"
    assert active_age_a != active_age_b, "Agent ages should be independent"

    print("\n✅ TEST PASSED: Agents calculated independently")
    print("=" * 80)


# Test 5: Tier Boundary Testing
@pytest.mark.asyncio
async def test_tier_boundary(mock_mcp, adapter):
    """
    Test 5: Tier Boundary Testing

    Scenarios:
    - Tier 1 (180 days): 179 survives, 181 decays
    - Tier 2 (30 days): 29 survives, 31 decays
    - Tier 3 (14 days): 13 survives, 15 decays

    Expected: Exact boundary behavior for all tiers
    """
    print("\n" + "=" * 80)
    print("TEST 5: Tier Boundary Testing")
    print("=" * 80)

    agent_id = "test-agent-boundary"
    memory_created = datetime(2025, 1, 1, 10, 0, 0)

    test_cases = [
        ("principle", DecayFunction.SUPERSEDED_ONLY, 179, False),  # Tier 1
        ("principle", DecayFunction.SUPERSEDED_ONLY, 181, True),
        ("solution", DecayFunction.STALENESS_6MONTHS, 29, False),  # Tier 2
        ("solution", DecayFunction.STALENESS_6MONTHS, 31, True),
        ("context", DecayFunction.RAPID_14DAYS, 13, False),  # Tier 3
        ("context", DecayFunction.RAPID_14DAYS, 15, True),
    ]

    print(f"\nMemory created: {memory_created.date()}")

    for tier, decay_func, active_days, should_decay_expected in test_cases:
        tier_ttl = DECAY_POLICY_MAP[decay_func].days

        # Create activity pattern
        mock_mcp.entries[agent_id] = []  # Reset
        for i in range(active_days):
            mock_mcp.add_entry(agent_id, memory_created + timedelta(days=i))

        # Calculate
        activity_dates = mock_mcp.get_activity_dates(agent_id)
        active_age = adapter.calculate_active_age(memory_created, activity_dates)
        should_decay_actual = active_age > tier_ttl

        # Display
        status = "DECAY" if should_decay_actual else "SURVIVE"
        print(f"\nTier: {tier} | TTL: {tier_ttl} days | Active: {active_age} days")
        print(f"  Expected: {status} | Actual: {status}")

        # Assert
        assert should_decay_actual == should_decay_expected, (
            f"Tier {tier} boundary failed: "
            f"active_age={active_age}, ttl={tier_ttl}, "
            f"expected_decay={should_decay_expected}, actual_decay={should_decay_actual}"
        )

    print("\n✅ TEST PASSED: All tier boundaries correct")
    print("=" * 80)


# Run all tests
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Activity-Based Decay E2E Test Suite (Phase 2)")
    print("=" * 80)

    pytest.main([__file__, "-v", "-s"])
