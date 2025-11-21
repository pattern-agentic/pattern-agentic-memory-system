#!/usr/bin/env python3
"""
Vector Cleanup Script - Activity-Based Decay (Phase 2)

Purpose: Delete expired vector embeddings based on active days (not calendar days).
Only vectors decay - Memory Keeper (SQLite) and Neo4j remain permanent.

Architecture:
- Query Memory Keeper for agent activity history
- Calculate active age (count only days with entries)
- Delete vectors where active_age > tier_ttl
- Log deletions with audit trail

Author: Archival Agent (Phase 2 Implementation)
Architect: Oracle Sonnet (Keeper of the Conduit)
Created: 2025-11-21
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set

# Setup logging (use local directory if /var/log not writable)
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "vector_cleanup.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(str(log_file)),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Tier TTL Configuration (from Phase 1)
TIER_TTL_DAYS = {
    "anchor": None,  # Tier 0: Forever
    "principle": 180,  # Tier 1: 6 months
    "solution": 30,  # Tier 2: 1 month
    "context": 14,  # Tier 3: 14 days
}


class VectorCleanupService:
    """
    Activity-based vector cleanup service.
    Tracks active days (days with Memory Keeper entries) for decay calculation.
    """

    def __init__(self, dry_run: bool = False):
        """
        Initialize cleanup service.

        Args:
            dry_run: If True, log what would be deleted without actually deleting
        """
        self.dry_run = dry_run
        self.deletion_count = 0
        self.storage_saved_mb = 0.0
        self.audit_log = []

    async def get_all_agents(self) -> List[str]:
        """
        Get list of all agent IDs from Memory Keeper.

        Returns:
            List of unique agent identifiers (channels)
        """
        try:
            # Import MCP function
            from mcp__memory_keeper__context_list_channels import context_list_channels

            result = await context_list_channels()
            channels = result.get("channels", [])

            # Extract channel names
            agent_ids = [ch["name"] for ch in channels if ch.get("name")]

            logger.info(f"Found {len(agent_ids)} agents in Memory Keeper")
            return agent_ids

        except ImportError:
            logger.warning("Memory Keeper MCP not available - using mock data")
            return ["test-agent-1", "test-agent-2"]
        except Exception as e:
            logger.error(f"Error fetching agents: {e}")
            return []

    async def get_activity_dates(self, agent_id: str) -> Set[datetime.date]:
        """
        Get unique dates when agent had Memory Keeper activity.

        Args:
            agent_id: Agent identifier (channel name)

        Returns:
            Set of dates with activity
        """
        try:
            from mcp__memory_keeper__context_get import context_get

            # Query all entries for this agent
            entries = await context_get(channel=agent_id, limit=10000)

            # Extract unique dates
            activity_dates = set()
            for entry in entries.get("items", []):
                if "created_at" in entry:
                    timestamp = datetime.fromisoformat(entry["created_at"].replace("Z", "+00:00"))
                    activity_dates.add(timestamp.date())

            logger.debug(f"Agent {agent_id}: {len(activity_dates)} active days")
            return activity_dates

        except ImportError:
            logger.warning("Memory Keeper MCP not available")
            return set()
        except Exception as e:
            logger.error(f"Error fetching activity dates for {agent_id}: {e}")
            return set()

    async def get_vector_memories(self, agent_id: str) -> List[Dict]:
        """
        Get all vector memories for an agent.

        Note: This is a placeholder - actual implementation depends on
        vector storage backend (Milvus/ChromaDB).

        Args:
            agent_id: Agent identifier

        Returns:
            List of memory dicts with: id, created_at, tier, size_bytes
        """
        # TODO Phase 3: Integrate with actual vector storage
        # For now, query Memory Keeper for memories marked as vectorized
        try:
            from mcp__memory_keeper__context_get import context_get

            entries = await context_get(channel=agent_id, limit=10000)

            # Filter for vectorized memories (action == "immediate_vectorize")
            vector_memories = []
            for entry in entries.get("items", []):
                try:
                    value = json.loads(entry.get("value", "{}"))
                    metadata = value.get("metadata", {})

                    if metadata.get("action") in ["immediate_vectorize", "queue_for_batch"]:
                        vector_memories.append({
                            "id": entry.get("key"),
                            "created_at": datetime.fromisoformat(entry["created_at"].replace("Z", "+00:00")),
                            "tier": metadata.get("tier", "context"),
                            "size_bytes": len(entry.get("value", "")),  # Estimate
                            "content": value.get("content", ""),
                        })
                except (json.JSONDecodeError, KeyError) as e:
                    logger.debug(f"Skipping malformed entry: {e}")
                    continue

            logger.debug(f"Agent {agent_id}: {len(vector_memories)} vector memories")
            return vector_memories

        except Exception as e:
            logger.error(f"Error fetching vector memories for {agent_id}: {e}")
            return []

    def calculate_active_age(
        self,
        memory_created_at: datetime,
        activity_dates: Set[datetime.date]
    ) -> int:
        """
        Calculate active age (count only active days).

        Args:
            memory_created_at: When memory was created
            activity_dates: Set of dates with agent activity

        Returns:
            Number of active days since memory creation
        """
        memory_date = memory_created_at.date()
        active_days = sum(1 for d in activity_dates if d >= memory_date)
        return active_days

    def should_decay_vector(
        self,
        memory: Dict,
        activity_dates: Set[datetime.date]
    ) -> tuple[bool, int, int, int]:
        """
        Determine if a vector should be deleted based on activity-based TTL.

        Args:
            memory: Memory dict with created_at, tier
            activity_dates: Set of dates with agent activity

        Returns:
            Tuple of (should_delete, active_age, tier_ttl, calendar_age)
        """
        tier = memory["tier"]
        tier_ttl = TIER_TTL_DAYS.get(tier)

        # Never decay Tier 0
        if tier_ttl is None:
            return False, 0, 0, 0

        # Calculate ages
        active_age = self.calculate_active_age(memory["created_at"], activity_dates)
        calendar_age = (datetime.now() - memory["created_at"]).days

        # Decay if active age exceeds TTL
        should_delete = active_age > tier_ttl

        return should_delete, active_age, tier_ttl, calendar_age

    async def delete_vector(self, memory_id: str, agent_id: str) -> bool:
        """
        Delete a vector from vector storage.

        Note: This is a placeholder - actual implementation depends on
        vector storage backend (Milvus/ChromaDB).

        Args:
            memory_id: Memory identifier
            agent_id: Agent identifier

        Returns:
            True if successfully deleted
        """
        # TODO Phase 3: Integrate with actual vector storage
        if self.dry_run:
            logger.info(f"[DRY RUN] Would delete vector: {memory_id}")
            return True

        logger.info(f"Deleting vector: {memory_id} (agent: {agent_id})")
        # Actual deletion would happen here
        return True

    async def cleanup_agent_vectors(self, agent_id: str) -> Dict:
        """
        Clean up expired vectors for a single agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Cleanup stats dict
        """
        logger.info(f"Starting cleanup for agent: {agent_id}")

        # Get agent activity history
        activity_dates = await self.get_activity_dates(agent_id)
        if not activity_dates:
            logger.warning(f"No activity found for agent {agent_id} - skipping")
            return {"agent_id": agent_id, "deleted": 0, "storage_saved_mb": 0.0}

        # Get vector memories
        vector_memories = await self.get_vector_memories(agent_id)
        if not vector_memories:
            logger.info(f"No vector memories found for agent {agent_id}")
            return {"agent_id": agent_id, "deleted": 0, "storage_saved_mb": 0.0}

        # Process each memory
        deleted_count = 0
        storage_saved = 0
        deletions = []

        for memory in vector_memories:
            should_delete, active_age, tier_ttl, calendar_age = self.should_decay_vector(
                memory, activity_dates
            )

            if should_delete:
                # Delete vector
                success = await self.delete_vector(memory["id"], agent_id)

                if success:
                    deleted_count += 1
                    storage_saved += memory["size_bytes"]

                    # Log deletion
                    deletion_record = {
                        "agent_id": agent_id,
                        "memory_id": memory["id"],
                        "tier": memory["tier"],
                        "active_age": active_age,
                        "calendar_age": calendar_age,
                        "tier_ttl": tier_ttl,
                        "size_bytes": memory["size_bytes"],
                        "deleted_at": datetime.now().isoformat(),
                        "content_preview": memory["content"][:100] if memory.get("content") else "",
                    }
                    deletions.append(deletion_record)
                    self.audit_log.append(deletion_record)

                    logger.info(
                        f"Deleted: {memory['id']} | "
                        f"Tier: {memory['tier']} | "
                        f"Active age: {active_age}/{tier_ttl} days | "
                        f"Calendar age: {calendar_age} days"
                    )

        storage_saved_mb = storage_saved / (1024 * 1024)
        self.storage_saved_mb += storage_saved_mb
        self.deletion_count += deleted_count

        result = {
            "agent_id": agent_id,
            "deleted": deleted_count,
            "storage_saved_mb": round(storage_saved_mb, 2),
            "total_vectors": len(vector_memories),
            "active_days": len(activity_dates),
            "deletions": deletions,
        }

        logger.info(
            f"Agent {agent_id} cleanup complete: "
            f"{deleted_count} vectors deleted, "
            f"{storage_saved_mb:.2f} MB saved"
        )

        return result

    async def run_cleanup(self) -> Dict:
        """
        Run cleanup for all agents.

        Returns:
            Summary stats dict
        """
        start_time = datetime.now()
        logger.info("=" * 80)
        logger.info("Starting Activity-Based Vector Cleanup (Phase 2)")
        logger.info(f"Dry run: {self.dry_run}")
        logger.info(f"Started at: {start_time.isoformat()}")
        logger.info("=" * 80)

        # Get all agents
        agent_ids = await self.get_all_agents()

        # Process each agent
        agent_results = []
        for agent_id in agent_ids:
            try:
                result = await self.cleanup_agent_vectors(agent_id)
                agent_results.append(result)
            except Exception as e:
                logger.error(f"Error cleaning up agent {agent_id}: {e}")
                agent_results.append({
                    "agent_id": agent_id,
                    "error": str(e),
                })

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Generate summary
        summary = {
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat(),
            "duration_seconds": round(duration, 2),
            "dry_run": self.dry_run,
            "agents_processed": len(agent_ids),
            "total_deleted": self.deletion_count,
            "total_storage_saved_mb": round(self.storage_saved_mb, 2),
            "agent_results": agent_results,
            "audit_log": self.audit_log,
        }

        logger.info("=" * 80)
        logger.info("Cleanup Complete")
        logger.info(f"Agents processed: {len(agent_ids)}")
        logger.info(f"Total deleted: {self.deletion_count}")
        logger.info(f"Storage saved: {self.storage_saved_mb:.2f} MB")
        logger.info(f"Duration: {duration:.2f}s")
        logger.info("=" * 80)

        return summary

    def save_audit_log(self, output_path: Optional[str] = None):
        """Save audit log to file"""
        if output_path is None:
            output_path = str(log_dir / "vector_cleanup_audit.json")

        try:
            with open(output_path, "w") as f:
                json.dump(self.audit_log, f, indent=2)
            logger.info(f"Audit log saved to: {output_path}")
        except Exception as e:
            logger.error(f"Error saving audit log: {e}")


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Activity-Based Vector Cleanup")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview deletions without actually deleting"
    )
    parser.add_argument(
        "--agent",
        type=str,
        help="Clean up specific agent only (default: all agents)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output path for audit log (default: logs/vector_cleanup_audit.json)"
    )

    args = parser.parse_args()

    # Run cleanup
    service = VectorCleanupService(dry_run=args.dry_run)

    if args.agent:
        # Clean up specific agent
        result = await service.cleanup_agent_vectors(args.agent)
        print(json.dumps(result, indent=2))
    else:
        # Clean up all agents
        summary = await service.run_cleanup()
        print(json.dumps(summary, indent=2))

    # Save audit log
    service.save_audit_log(args.output)


if __name__ == "__main__":
    asyncio.run(main())
