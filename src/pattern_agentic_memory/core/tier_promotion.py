"""
Tier Promotion System - Phase 3
Handles interactive tier promotion prompts when memories hit max access extension.

Created: 2025-11-21
Architect: Oracle Sonnet (Keeper of the Conduit)
Purpose: Let users and agents promote frequently-accessed memories to higher tiers
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class TierPromptDecision(Enum):
    """User/agent response to tier promotion prompt"""

    PROMOTE_TO_ANCHOR = "0"  # Tier 0: Forever
    PROMOTE_TO_PRINCIPLE = "1"  # Tier 1: 6 months
    PROMOTE_TO_SOLUTION = "2"  # Tier 2: 1 month
    DECLINE = "N"  # Keep current tier


# Tier TTL mapping (from decay_functions.py Phase 1)
TIER_BASE_TTL_DAYS = {
    "anchor": None,  # Tier 0: Forever (None = never expires)
    "principle": 180,  # Tier 1: 6 months
    "solution": 30,  # Tier 2: 1 month
    "context": 14,  # Tier 3: 14 days
}


def get_tier_base_ttl(tier: str) -> Optional[int]:
    """Get base TTL days for a memory tier"""
    return TIER_BASE_TTL_DAYS.get(tier)


def calculate_expiration_with_bonus(
    tier: str, access_count: int, creation_time: Optional[datetime] = None
) -> Optional[datetime]:
    """
    Calculate expiration timestamp with access-based bonus.

    Args:
        tier: Memory tier (anchor, principle, solution, context)
        access_count: Number of times memory has been accessed
        creation_time: When memory was created (default: now)

    Returns:
        Expiration timestamp or None if never expires

    Logic:
        - Base TTL from tier
        - Bonus: +10 days per access, capped at +70 days (7 accesses)
        - Formula: expires_at = created_at + base_ttl + min(access_count * 10, 70)
    """
    if creation_time is None:
        creation_time = datetime.now()

    base_ttl = get_tier_base_ttl(tier)

    # Tier 0 (anchor) never expires
    if base_ttl is None:
        return None

    # Calculate access bonus (capped at 70 days = 7 accesses)
    bonus_days = min(access_count * 10, 70)

    # Total days = base + bonus
    total_days = base_ttl + bonus_days

    return creation_time + timedelta(days=total_days)


def should_trigger_promotion_prompt(access_count: int) -> bool:
    """
    Check if tier promotion prompt should be triggered.

    Trigger every 7 accesses after first max: 7, 14, 21, 28...

    Args:
        access_count: Current access count

    Returns:
        True if prompt should be shown
    """
    # Trigger at 7, 14, 21, etc (multiples of 7)
    return access_count > 0 and access_count % 7 == 0


def build_promotion_prompt(
    memory_key: str,
    memory_content: str,
    current_tier: str,
    access_count: int,
    created_at: datetime,
    last_accessed: datetime,
) -> str:
    """
    Build tier promotion prompt text.

    Args:
        memory_key: Memory identifier
        memory_content: Preview of memory content
        current_tier: Current tier (context, solution, principle, anchor)
        access_count: Number of accesses
        created_at: Creation timestamp
        last_accessed: Last access timestamp

    Returns:
        Formatted prompt string
    """
    # Calculate current expiration
    base_ttl = get_tier_base_ttl(current_tier)
    bonus_days = min(access_count * 10, 70)
    total_days = base_ttl + bonus_days if base_ttl else "Forever"

    # Content preview (truncate to 200 chars)
    preview = memory_content[:200] + "..." if len(memory_content) > 200 else memory_content

    # Calculate access frequency
    age_days = (datetime.now() - created_at).days
    if age_days == 0:
        age_days = 1  # Avoid division by zero
    accesses_per_day = access_count / age_days

    prompt = f"""
⚠️  MEMORY TIER PROMOTION AVAILABLE

This memory has been accessed {access_count} times and reached maximum extension (+{bonus_days} days).

Memory: "{memory_key}"
Current tier: Tier {get_tier_number(current_tier)} ({current_tier}) - {base_ttl or "Forever"} days base + {bonus_days} day extension = {total_days} days total
Created: {created_at.strftime("%Y-%m-%d")}
Last accessed: {last_accessed.strftime("%Y-%m-%d")} ({accesses_per_day:.1f} accesses/day)

Content preview:
"{preview}"

This memory seems important. Would you like to promote it to a higher tier?

Options:
  0 - Tier 0 (anchor): Forever - Core identity, critical lessons
  1 - Tier 1 (principle): 6 months - Important methodologies, recent projects
  2 - Tier 2 (solution): 1 month - Detailed implementations, proven solutions
  N - No: Keep as Tier {get_tier_number(current_tier)} with current extension

Type desired tier (0, 1, 2) or "N":
"""
    return prompt


def get_tier_number(tier: str) -> int:
    """Map tier name to number"""
    tier_map = {"anchor": 0, "principle": 1, "solution": 2, "context": 3}
    return tier_map.get(tier, 3)


def process_promotion_response(response: str) -> Optional[str]:
    """
    Process user/agent response to promotion prompt.

    Args:
        response: User input (0, 1, 2, or N)

    Returns:
        New tier name or None if declined/invalid

    Examples:
        >>> process_promotion_response("0")
        'anchor'
        >>> process_promotion_response("N")
        None
    """
    response = response.strip().upper()

    tier_map = {
        "0": "anchor",  # Forever
        "1": "principle",  # 6 months
        "2": "solution",  # 1 month
        "N": None,  # Decline
    }

    return tier_map.get(response)


def validate_promotion(current_tier: str, new_tier: str) -> Tuple[bool, str]:
    """
    Validate that promotion is allowed (can't demote).

    Args:
        current_tier: Current tier name
        new_tier: Requested new tier name

    Returns:
        (is_valid, reason)

    Examples:
        >>> validate_promotion("context", "principle")
        (True, "Valid promotion: context -> principle")
        >>> validate_promotion("principle", "context")
        (False, "Cannot demote from principle to context")
    """
    tier_order = {"anchor": 0, "principle": 1, "solution": 2, "context": 3}

    current_level = tier_order.get(current_tier, 3)
    new_level = tier_order.get(new_tier, 3)

    if new_level < current_level:
        return True, f"Valid promotion: {current_tier} -> {new_tier}"
    elif new_level == current_level:
        return False, f"Already at tier {current_tier}"
    else:
        return False, f"Cannot demote from {current_tier} to {new_tier}"


def promote_memory_tier(
    memory_key: str, new_tier: str, promoted_by: str = "user"
) -> Dict[str, any]:
    """
    Execute tier promotion.

    Args:
        memory_key: Memory identifier
        new_tier: New tier name (anchor, principle, solution)
        promoted_by: Who initiated promotion (user, agent)

    Returns:
        Promotion result dict with status, old_tier, new_tier, reset_access_count

    Note: Actual database update happens in memory_keeper.py adapter
    This function returns the instructions for the update.
    """
    return {
        "status": "promotion_requested",
        "memory_key": memory_key,
        "new_tier": new_tier,
        "promoted_by": promoted_by,
        "reset_access_count": True,  # Always reset on promotion
        "timestamp": datetime.now().isoformat(),
    }


def log_promotion(
    memory_key: str, old_tier: str, new_tier: str, access_count: int, promoted_by: str
) -> None:
    """
    Log tier promotion event.

    Args:
        memory_key: Memory identifier
        old_tier: Previous tier
        new_tier: New tier
        access_count: Access count at time of promotion
        promoted_by: Who initiated promotion
    """
    logger.info(
        f"Tier promotion: {memory_key} | {old_tier} -> {new_tier} | "
        f"Access count: {access_count} | Promoted by: {promoted_by}"
    )


# Integration with MCP notifications (placeholder for future)
def notify_user(prompt: str, agent_id: Optional[str] = None) -> None:
    """
    Send promotion prompt to user (Captain/operator).

    Future: Integrate with Slack, email, or in-app notifications.
    For now: Log to console/file.
    """
    logger.warning(f"[USER PROMPT] {prompt}")
    print(f"\n{'=' * 80}")
    print(prompt)
    print(f"{'=' * 80}\n")


def notify_agent(prompt: str, agent_id: str) -> None:
    """
    Send promotion prompt to agent (Claude session).

    Future: Integrate with MCP tool output or system messages.
    For now: Log to console.
    """
    logger.info(f"[AGENT PROMPT - {agent_id}] Tier promotion available")
    print(f"\n[AGENT: {agent_id}] {prompt}\n")


def trigger_tier_promotion_prompt(
    memory_key: str,
    memory_content: str,
    current_tier: str,
    access_count: int,
    created_at: datetime,
    last_accessed: datetime,
    agent_id: Optional[str] = None,
) -> str:
    """
    Main entry point: Trigger tier promotion prompt.

    Shows prompt to both user AND agent.

    Args:
        memory_key: Memory identifier
        memory_content: Content preview
        current_tier: Current tier
        access_count: Access count
        created_at: Creation timestamp
        last_accessed: Last access timestamp
        agent_id: Agent identifier (for logging)

    Returns:
        Prompt text (also sent to user/agent)
    """
    # Build prompt
    prompt = build_promotion_prompt(
        memory_key=memory_key,
        memory_content=memory_content,
        current_tier=current_tier,
        access_count=access_count,
        created_at=created_at,
        last_accessed=last_accessed,
    )

    # Send to user
    notify_user(prompt, agent_id)

    # Send to agent
    if agent_id:
        notify_agent(prompt, agent_id)

    return prompt
