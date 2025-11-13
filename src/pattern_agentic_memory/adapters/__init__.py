"""
Pattern Agentic Memory System - Adapters Module

Adapters for integrating the core memory system with external storage backends.

Public API exports:
- MemoryKeeperAdapter: Integration with Memory Keeper MCP
- Neo4jWorkingMemory: Working memory storage in Neo4j graph
"""

from .memory_keeper import MemoryKeeperAdapter
from .neo4j_working import Neo4jWorkingMemory

__all__ = [
    "MemoryKeeperAdapter",
    "Neo4jWorkingMemory",
]
