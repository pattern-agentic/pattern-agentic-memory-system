"""
Decay strategies for different memory tiers.

Extracted from adaptive_memory_system.py as part of Pattern Agentic Memory System extraction.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class DecayFunction(Enum):
    """Decay strategies for different memory tiers"""

    NEVER = "never"  # Tier 0
    SUPERSEDED_ONLY = "superseded_only"  # Tier 1
    STALENESS_6MONTHS = "staleness_6months"  # Tier 2
    RAPID_7DAYS = "rapid_7days"  # Tier 3
    RAPID_24HOURS = "rapid_24hours"  # Tier 3 (ephemeral)


# Decay policy mapping
DECAY_POLICY_MAP = {
    DecayFunction.NEVER: None,  # Never expires
    DecayFunction.SUPERSEDED_ONLY: None,  # Manual removal only
    DecayFunction.STALENESS_6MONTHS: timedelta(days=180),
    DecayFunction.RAPID_7DAYS: timedelta(days=7),
    DecayFunction.RAPID_24HOURS: timedelta(hours=24),
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
