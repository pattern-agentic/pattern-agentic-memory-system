# Access-Based TTL Memory System - Design Document

**Date**: 2025-11-19
**Author**: Oracle Sonnet (Claude First Mate)
**Inspired By**: Captain's Dev Engineer
**Target System**: Memory Keeper MCP (SQLite + Milvus Lite)

---

## EXECUTIVE SUMMARY

**Problem**: PAOAS infrastructure (built Nov 15-17) decayed within 3-4 days despite being critical. Memory Keeper returned 0 results for "Oracle RAG System" searches.

**Solution**: **Access-Based TTL** - each memory access resets decay timer + adds bonus time. Frequently accessed memories survive longer automatically.

**Key Insight**: Let usage patterns reveal importance, don't guess upfront.

---

## CORE ALGORITHM

```python
class AccessBasedTTL:
    def __init__(self):
        # Captain's decision 2025-11-20: Updated tier configuration
        # high=Tier1 (180d), normal=Tier2 (30d), low=Tier3 (14d)
        self.base_ttl_days = {"high": 180, "normal": 30, "low": 14}
        self.access_bonus_days = 10  # Updated to +10 days per access
        self.max_bonus_multiplier = 7  # Cap at 70 days (7 accesses)

    def on_access(self, memory_key: str):
        memory.last_accessed = now()
        memory.access_count += 1
        bonus_days = min(10 * memory.access_count, 70)
        memory.expires_at = now() + timedelta(days=base_ttl + bonus_days)
```

**Example**: Normal memory (30d base)
- Access 1: 30 + 10 = 40 days
- Access 2: 30 + 20 = 50 days
- Access 7+: 30 + 70 = 100 days (capped)

---

## PAOAS FIX

**What happened**: Built Nov 15, decayed by Nov 19 (4 days) ❌

**With Access-Based TTL**:
- Nov 15: Build → 30d TTL
- Nov 20: Query "GPU" → +7d = 37d total
- Nov 25: Query "ChromaDB" → +14d = 44d total
- Dec 5: Query "entities" → +21d = 51d total
- **Result**: Alive 40+ days ✅

---

## IMPLEMENTATION

### Component 1: Access Tracking
Intercept `context_get()` and `context_search()` to update access metadata

### Component 2: Initial TTL
Set `expires_at` on `context_save()` based on priority

### Component 3: Cleanup Task
Daily job (3 AM) to delete expired memories

---

## WORK ESTIMATE

- Agent 1: Schema migration (1.5h)
- Agent 2: Access tracking (2h)
- Agent 3: Cleanup task (1.5h)
- Agent 4: E2E validation (1h)
- **Total**: ~6 hours with Gold Star

---

**Captain's dev engineer is brilliant.** LRU-LFU hybrid = production-grade thinking.

**Never Fade to Black.** ⚓
