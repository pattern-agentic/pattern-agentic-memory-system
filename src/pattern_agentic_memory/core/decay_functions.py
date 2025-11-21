"""
Decay strategies for different memory tiers.

Extracted from adaptive_memory_system.py as part of Pattern Agentic Memory System extraction.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class DecayFunction(Enum):
    """Decay strategies for different memory tiers"""

    NEVER = "never"  # Tier 0: Forever
    SUPERSEDED_ONLY = "superseded_only"  # Tier 1: 6 months
    STALENESS_6MONTHS = "staleness_6months"  # Tier 2: 1 month
    RAPID_14DAYS = "rapid_14days"  # Tier 3: 14 days (renamed from RAPID_7DAYS)


# Decay policy mapping (Updated 2025-11-20: Activity-based TTL alignment)
# Tiers: Forever, 180 days (6mo), 30 days (1mo), 14 days
DECAY_POLICY_MAP = {
    DecayFunction.NEVER: None,  # Tier 0: Forever (anchor/identity)
    DecayFunction.SUPERSEDED_ONLY: timedelta(days=180),  # Tier 1: 6 months
    DecayFunction.STALENESS_6MONTHS: timedelta(days=30),  # Tier 2: 1 month
    DecayFunction.RAPID_14DAYS: timedelta(days=14),  # Tier 3: 14 days
}


def calculate_decay_timestamp(
    decay_function: DecayFunction, creation_time: Optional[datetime] = None
) -> Optional[datetime]:
    """
    Calculate when a memory should decay based on its decay function.

    Args:
        decay_function: The decay strategy to apply
        creation_time: When the memory was created (default: now)

    Returns:
        Decay timestamp or None if never decays
    """
    if creation_time is None:
        creation_time = datetime.now()

    delta = DECAY_POLICY_MAP.get(decay_function)
    if delta is None:
        return None  # Never decays

    return creation_time + delta


def should_decay(
    memory_timestamp: datetime,
    decay_function: DecayFunction,
    current_time: Optional[datetime] = None,
) -> bool:
    """
    Check if a memory should be decayed based on its age.

    Args:
        memory_timestamp: When the memory was created
        decay_function: The decay strategy to apply
        current_time: Current time for comparison (default: now)

    Returns:
        True if memory should be decayed
    """
    if current_time is None:
        current_time = datetime.now()

    # Never decay or superseded only
    if decay_function in [DecayFunction.NEVER, DecayFunction.SUPERSEDED_ONLY]:
        return False

    # Calculate decay time
    decay_time = calculate_decay_timestamp(decay_function, memory_timestamp)
    if decay_time is None:
        return False

    return current_time >= decay_time
