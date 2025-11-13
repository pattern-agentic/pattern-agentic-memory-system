"""
Unit Tests for User Memory Command Parser
Part of Gate 1: Functional Completeness

Tests the UserMemoryCommandParser component:
- Command detection (remember, save, lesson learned, important, etc)
- User command vs implicit teaching patterns
- Scope determination (full_conversation vs current_message)
- No command detection
- Confidence scoring

Migrated from: tests/test_adaptive_memory_system.py
"""

from pattern_agentic_memory.core.command_parser import UserMemoryCommandParser


class TestUserMemoryCommandParser:
    """Gate 1: Functional Completeness - Command Detection"""

    def test_remember_this_command(self):
        """'remember this' command detected"""
        parser = UserMemoryCommandParser()

        result = parser.parse_user_intent("Remember this important pattern")

        assert result is not None
        assert result["action"] == "immediate_save"
        assert result["user_commanded"] is True
        assert result["confidence"] >= 0.9

    def test_save_this_command(self):
        """'save this' command detected"""
        parser = UserMemoryCommandParser()

        result = parser.parse_user_intent("Save this configuration for later")

        assert result is not None
        assert result["action"] == "immediate_save"
        assert result["user_commanded"] is True

    def test_lesson_learned_command(self):
        """'lesson learned' command detected"""
        parser = UserMemoryCommandParser()

        result = parser.parse_user_intent("Lesson learned: always validate first")

        assert result is not None
        assert result["action"] == "save_as_validation"
        assert result["user_commanded"] is True

    def test_this_is_important_command(self):
        """'this is important' command detected"""
        parser = UserMemoryCommandParser()

        result = parser.parse_user_intent("This is important information")

        assert result is not None
        assert result["action"] == "priority_save"
        assert result["user_commanded"] is True

    def test_always_do_this_command(self):
        """'always do this' command detected"""
        parser = UserMemoryCommandParser()

        result = parser.parse_user_intent("Always do this when deploying")

        assert result is not None
        assert result["action"] == "save_as_rule"
        assert result["user_commanded"] is True

    def test_never_do_that_command(self):
        """'never do that' command detected"""
        parser = UserMemoryCommandParser()

        result = parser.parse_user_intent("Never do that without testing")

        assert result is not None
        assert result["action"] == "save_as_constraint"
        assert result["user_commanded"] is True

    def test_critical_command(self):
        """'critical' command detected"""
        parser = UserMemoryCommandParser()

        result = parser.parse_user_intent("Critical: Update security settings")

        assert result is not None
        assert result["action"] == "priority_save"
        assert result["user_commanded"] is True

    def test_forget_that_command(self):
        """'forget that' command detected"""
        parser = UserMemoryCommandParser()

        result = parser.parse_user_intent("Forget that previous instruction")

        assert result is not None
        assert result["action"] == "mark_for_deletion"
        assert result["user_commanded"] is True

    def test_no_command_detection(self):
        """Regular message without commands returns None"""
        parser = UserMemoryCommandParser()

        result = parser.parse_user_intent("This is just regular conversation about the weather")

        # Should return None or a low-confidence result
        if result is not None:
            assert result["confidence"] < 0.9

    def test_implicit_teaching_pattern(self):
        """Implicit teaching patterns detected with lower confidence"""
        parser = UserMemoryCommandParser()

        result = parser.parse_user_intent("You should always check the logs before debugging")

        assert result is not None
        assert result["action"] == "potential_lesson"
        assert result["confidence"] < 0.9
        assert result["user_commanded"] is False

    def test_scope_determination_conversation(self):
        """Scope determined correctly for conversation context"""
        parser = UserMemoryCommandParser()

        result = parser.parse_user_intent("Remember this conversation")

        assert result is not None
        assert result["scope"] == "full_conversation"

    def test_scope_determination_current_message(self):
        """Scope determined correctly for current message"""
        parser = UserMemoryCommandParser()

        result = parser.parse_user_intent("Save this for later")

        assert result is not None
        assert result["scope"] == "current_message"
