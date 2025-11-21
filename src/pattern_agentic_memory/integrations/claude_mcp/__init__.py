"""
Claude MCP integration for Pattern Agentic Memory System.

This module provides Claude Code/Desktop-specific adapters and helpers for
deploying the adaptive memory system in Model Context Protocol environments.

Created: 2025-11-13
Architecture: Pattern Agentic Memory System
Platform: Claude Code with MCP
"""

from typing import Dict, Optional

from ...adapters.memory_keeper import MemoryKeeperAdapter
from ...core.memory_system import AdaptiveMemoryOrchestrator
from .command_detector import ClaudeCommandDetector
from .identity_anchor import IdentityAnchorManager
from .mcp_wrapper import MCPMemoryWrapper

__all__ = [
    "MCPMemoryWrapper",
    "ClaudeCommandDetector",
    "IdentityAnchorManager",
    "setup_claude_memory_system",
]


def setup_claude_memory_system(
    config: Optional[Dict] = None,
) -> MCPMemoryWrapper:
    """
    Initialize adaptive memory system for Claude MCP environments.

    This is the main entry point for Claude-based agents using the
    Pattern Agentic Memory System. It provides:
    - Natural language command detection
    - Identity anchor preservation across sessions
    - MCP-optimized memory operations

    Args:
        config: Optional configuration dict with keys:
            - enable_identity_anchors: bool (default True)
            - enable_command_detection: bool (default True)
            - memory_keeper_session_id: str (optional)

    Returns:
        Configured MCPMemoryWrapper ready for use

    Example:
        >>> memory = setup_claude_memory_system()
        >>> decision = await memory.process_user_message(
        ...     "Remember this: Always use ruff for formatting"
        ... )
        >>> print(decision["action"])  # "immediate_vectorize"
    """
    config = config or {}

    # Create orchestrator and adapter
    orchestrator = AdaptiveMemoryOrchestrator()
    adapter = MemoryKeeperAdapter()

    # Create MCP wrapper with Claude-specific features
    wrapper = MCPMemoryWrapper(
        orchestrator=orchestrator,
        adapter=adapter,
        enable_identity_anchors=config.get("enable_identity_anchors", True),
        enable_command_detection=config.get("enable_command_detection", True),
    )

    return wrapper
