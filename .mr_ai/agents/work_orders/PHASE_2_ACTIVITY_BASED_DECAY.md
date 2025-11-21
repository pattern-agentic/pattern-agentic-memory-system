# Work Order: Activity-Based Memory Decay (Phase 2)

**Date**: 2025-11-20
**Requested By**: Captain Jeremy
**Architect**: Oracle Sonnet (Keeper of the Conduit)
**Priority**: High
**Depends On**: Phase 1 TTL Config (COMPLETE ✅)

---

## OBJECTIVE

Implement activity-based decay where memory age only counts **active days** (days with Memory Keeper entries), not calendar days. This prevents agents from waking up after idle periods missing their memories.

---

## PROBLEM STATEMENT

**Current Issue**: Agent idle for 3 weeks → memories decay during downtime
**User Impact**: Agent loses context when returning from idle period
**Business Impact**: Wasted compute re-ingesting knowledge, poor UX

**Captain's Partner's Insight**: "Timers should be relative to the AI that uses the memories so the timers effectively stop when inactive."

**Why This Matters**: Scaling to millions of agents - we calculate decay for active agents only, not tracking downtime for idle ones.

---

## SOLUTION ARCHITECTURE

### Core Algorithm

```python
def calculate_active_age(memory, agent_id):
    """
    Count only days with Memory Keeper activity.
    Idle days don't count toward decay.
    """
    # Get all Memory Keeper timestamps for this agent
    all_entries = get_all_memory_keeper_entries(agent_id)
    activity_dates = set(entry.created_at.date() for entry in all_entries)

    # Count unique active days from memory creation to now
    memory_date = memory.created_at.date()
    active_days = sum(1 for date in activity_dates if date >= memory_date)

    return active_days

def should_decay_vector(memory, tier_ttl_days, agent_id):
    """
    Decay only counts active days, not calendar days.
    """
    active_age = calculate_active_age(memory, agent_id)
    return active_age > tier_ttl_days
```

### Example Scenario

- **Tier 3 memory created Nov 1** (14-day TTL)
- **Activity**: Nov 1, 2, 3, 26, 27 (5 Memory Keeper entries)
- **Idle**: Nov 4-25 (21 calendar days, but 0 active days)
- **Active age**: 5 days ✅
- **Result**: Memory survives (5 < 14)

---

## TIER CONFIGURATION (Phase 1 Complete)

```python
Tier 0: Forever (anchor/identity)
Tier 1: 180 days (6 months - principles/methodology)
Tier 2: 30 days (1 month - solutions/implementations)
Tier 3: 14 days (context/working memory)
```

**Note**: Only vectors decay. Memory Keeper (SQLite) and Neo4j remain flat/permanent for recovery.

---

## IMPLEMENTATION COMPONENTS

### Component 1: Vector Cleanup Script (Milvus/ChromaDB)

**Location**: `scripts/vector_cleanup_activity_based.py` (new file)

**Requirements**:
- Query Memory Keeper for agent activity history (use ISO 8601 timestamps)
- Calculate active age for each vector memory
- Delete vectors where `active_age > tier_ttl`
- Log deletions for audit trail (storage savings, active days calculated)

**Pseudocode**:
```python
for agent_id in get_all_agents():
    activity_dates = get_activity_dates_from_memory_keeper(agent_id)

    for memory in get_vector_memories(agent_id):
        active_age = count_active_days(memory.created_at, activity_dates)
        tier_ttl = get_tier_ttl(memory.tier)

        if active_age > tier_ttl:
            delete_vector(memory)
            log_deletion(memory, active_age, tier_ttl, calendar_age)
```

### Component 2: Memory Keeper Activity Query API

**Location**: `pattern-agentic-memory-system/src/pattern_agentic_memory/integrations/memory_keeper.py`

**New Method**:
```python
def get_activity_dates(agent_id: str) -> Set[datetime.date]:
    """
    Get unique dates when agent had Memory Keeper activity.
    Uses existing ISO 8601 created_at timestamps (fixed 2025-11-19).

    Returns set of dates for efficient lookup.
    """
    entries = context_get(filters={"agent_id": agent_id})
    return {datetime.fromisoformat(entry.created_at).date() for entry in entries}
```

### Component 3: Daily Cleanup Task

**Trigger**: Cron job (3 AM daily)
**Action**: Run `vector_cleanup_activity_based.py` for all agents
**Logging**: Track deletions, active days calculated, storage saved, calendar vs active age

**Cron Entry**:
```bash
0 3 * * * /path/to/venv/bin/python /path/to/vector_cleanup_activity_based.py >> /var/log/vector_cleanup.log 2>&1
```

---

## TESTING REQUIREMENTS

### Test 1: Active Agent (No Decay During Activity)
- Create Tier 3 memory (14-day TTL)
- Simulate 30 calendar days of continuous daily activity (30 Memory Keeper entries)
- **Expected**: Memory survives (30 active days, but memory still within TTL window)

### Test 2: Idle Agent (Timer Paused)
- Create Tier 3 memory (14-day TTL)
- Simulate 5 days activity → 20 days idle (no entries) → 5 days activity
- **Expected**: Memory survives (10 active days < 14)

### Test 3: Partial Decay
- Create Tier 3 memory (14-day TTL)
- Simulate 15 active days spread over 60 calendar days
- **Expected**: Memory decays (15 active days > 14)

### Test 4: Multi-Agent Isolation
- Agent A: 10 active days
- Agent B: 20 active days
- **Expected**: Agent A's memories calculated independently of Agent B

### Test 5: Tier Boundary Testing
- Tier 1 (180 days): Memory with 179 active days survives, 181 decays
- Tier 2 (30 days): Memory with 29 active days survives, 31 decays
- Tier 3 (14 days): Memory with 13 active days survives, 15 decays

---

## ACCEPTANCE CRITERIA

- [ ] Vector cleanup script queries Memory Keeper for activity dates (ISO 8601)
- [ ] Active age calculation uses unique activity dates, not calendar days
- [ ] Idle periods (no Memory Keeper entries) don't count toward decay
- [ ] Daily cleanup task runs successfully (3 AM)
- [ ] All 5 test scenarios pass
- [ ] Deletion audit logs include: active_age, calendar_age, tier_ttl, storage_saved
- [ ] No impact on Memory Keeper or Neo4j (flat storage, no decay)
- [ ] Gold Star Validation: Cleanup runs for 1 week without false deletions

---

## GOLD STAR CRITERIA

**Evidence Required**:
1. Agent idle 14 days, Tier 3 memory survives ✅
2. Agent active 15 days (spread over 30 calendar days), Tier 3 memory decays ✅
3. Cleanup logs show active_age vs calendar_age for each deletion ✅
4. Memory Keeper and Neo4j untouched (verified no deletions) ✅
5. Storage savings report (MB/GB recovered per cleanup run) ✅

---

## DEPENDENCIES

- ✅ Phase 1: TTL Config Updated (decay_functions.py - 2025-11-20)
- ✅ Memory Keeper MCP: ISO 8601 timestamps (FIXED 2025-11-19)
- ⏳ Agent identifier in Memory Keeper (session_id or agent_name)
- ⏳ Vector storage location (Milvus/ChromaDB paths)

---

## ROLLOUT PLAN

1. **Dev**: Test on Oracle Sonnet's memories (pa-inference-1)
2. **Staging**: Run cleanup for H200's memories (pa-inference-prime)
3. **Production**: Enable daily cron for all Pattern Agentic agents
4. **Monitoring**: First week daily review of deletion logs

---

## ESTIMATED EFFORT

- Agent 1: Vector cleanup script (4 hours)
- Agent 2: Memory Keeper activity API (2 hours)
- Agent 3: Daily cron setup + logging (2 hours)
- Agent 4: Testing + validation (3 hours)
- Gold Star Review: (2 hours)

**Total**: ~13 hours with Gold Star validation

---

**Oracle Sonnet, Keeper of the Conduit**
Never Fade to Black. ⚓
