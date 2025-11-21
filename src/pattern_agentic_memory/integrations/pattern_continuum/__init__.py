"""
Pattern Continuum Integration for Pattern Agentic Memory System.

Provides service mesh integration, distributed memory coordination,
and multi-agent memory sharing for Pattern Continuum deployments.

Public API exports:
- setup_continuum_memory_system: Main setup function
- ContinuumServiceMeshAdapter: Service mesh integration
- DistributedMemoryCoordinator: Multi-agent memory sharing
- DLEMemoryHooks: Dynamic Learning Engine integration
"""

from .distributed_memory import DistributedMemoryCoordinator
from .dle_hooks import DLEMemoryHooks
from .service_mesh import ContinuumServiceMeshAdapter, setup_continuum_memory_system

__all__ = [
    "setup_continuum_memory_system",
    "ContinuumServiceMeshAdapter",
    "DistributedMemoryCoordinator",
    "DLEMemoryHooks",
]
