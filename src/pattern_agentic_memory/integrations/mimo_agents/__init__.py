"""
mimo agents integration for Pattern Agentic Memory System.

This module provides lightweight, resource-efficient adapters for
deploying the adaptive memory system in mimo-7b-rl agent environments.

Created: 2025-11-13
Architecture: Pattern Agentic Memory System
Platform: mimo-7b-rl agents (Pattern Agentic lightweight agents)
"""

from typing import Dict, Optional

from ...adapters.memory_keeper import MemoryKeeperAdapter
from ...core.memory_system import AdaptiveMemoryOrchestrator
from .async_memory import AsyncMemoryManager
from .command_interface import MimoCommandInterface
from .lightweight_wrapper import LightweightMemoryWrapper

__all__ = [
    "LightweightMemoryWrapper",
    "AsyncMemoryManager",
    "MimoCommandInterface",
    "setup_mimo_memory_system",
]


def setup_mimo_memory_system(
    config: Optional[Dict] = None,
) -> LightweightMemoryWrapper:
    """
    Initialize adaptive memory system for mimo-7b-rl agents.

    This is the main entry point for mimo-based agents. It provides:
    - Lightweight memory footprint (optimized for 7B param models)
    - Fast tier classification (minimal inference overhead)
    - Async/await support for non-blocking operations
    - Structured command interface (no NL parsing overhead)

    Args:
        config: Optional configuration dict with keys:
            - enable_async: bool (default True)
            - max_working_memory: int (default 100 items)
            - batch_threshold: int (default 25, lower than Claude)

    Returns:
        Configured LightweightMemoryWrapper ready for use

    Example:
        >>> memory = setup_mimo_memory_system()
        >>> decision = await memory.save_memory(
        ...     content="Fixed auth bug with token refresh",
        ...     tier="solution"
        ... )
        >>> print(decision["action"])  # "queue_for_batch"
    """
    config = config or {}

    # Create orchestrator and adapter
    orchestrator = AdaptiveMemoryOrchestrator()
    adapter = MemoryKeeperAdapter()

    # Create lightweight wrapper
    wrapper = LightweightMemoryWrapper(
        orchestrator=orchestrator,
        adapter=adapter,
        max_working_memory=config.get("max_working_memory", 100),
        batch_threshold=config.get("batch_threshold", 25),
    )

    return wrapper
