"""
Oracle Opus's user command detection.
Detects when users explicitly want something saved.

Extracted from adaptive_memory_system.py as part of Pattern Agentic Memory System extraction.
"""

import re
from typing import Any, Dict, Optional


class UserMemoryCommandParser:
    """
    Oracle Opus's user command detection.
    Detects when users explicitly want something saved.
    """

    MEMORY_COMMANDS = {
        "save this": "immediate_save",
        "remember this": "immediate_save",
        "remember this conversation": "save_context",
        "forget that": "mark_for_deletion",
        "this is important": "priority_save",
        "lesson learned": "save_as_validation",
        "always do this": "save_as_rule",
        "never do that": "save_as_constraint",
        "never forget": "immediate_save",
        "critical": "priority_save",
    }

    # Separate pattern-based rules (checked after exact matches)
    RULE_PATTERNS = [
        (r"^always\s+\w+", "save_as_rule"),  # "Always validate..." (must start sentence)
        (r"^never\s+(?!fade)", "save_as_constraint"),  # "Never skip..." (but not "Never Fade")
    ]

    def parse_user_intent(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Detect explicit memory commands in natural language.

        Returns:
            {action, confidence, scope} dict or None
        """
        message_lower = message.lower()

        # Check for explicit commands
        for trigger, action in self.MEMORY_COMMANDS.items():
            if trigger in message_lower:
                return {
                    "action": action,
                    "confidence": 0.9,
                    "scope": self._determine_scope(message, trigger),
                    "user_commanded": True,
                }

        # Check for pattern-based rules (e.g., "Always [action]", "Never [action]")
        for pattern, action in self.RULE_PATTERNS:
            if re.search(pattern, message_lower):
                return {
                    "action": action,
                    "confidence": 0.85,
                    "scope": "current_message",
                    "user_commanded": True,
                }

        # Check for implicit memory cues
        if self._contains_teaching_pattern(message):
            return {
                "action": "potential_lesson",
                "confidence": 0.6,
                "scope": "recent_interaction",
                "user_commanded": False,
            }

        return None

    def _determine_scope(self, message: str, trigger: str) -> str:
        """Determine what scope the memory command applies to"""
        if "conversation" in message.lower():
            return "full_conversation"
        elif "this" in message.lower():
            return "current_message"
        else:
            return "recent_context"

    def _contains_teaching_pattern(self, message: str) -> bool:
        """Check if message contains implicit teaching patterns"""
        teaching_patterns = [
            r"you should always",
            r"make sure to",
            r"don\'t forget to",
            r"remember to",
            r"next time",
            r"in the future",
        ]

        message_lower = message.lower()
        return any(re.search(pattern, message_lower) for pattern in teaching_patterns)
