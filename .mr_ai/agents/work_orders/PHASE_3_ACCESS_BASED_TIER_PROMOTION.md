# Work Order: Access-Based Tier Promotion (Phase 3)

**Date**: 2025-11-20 (Updated: 2025-11-22)
**Requested By**: Captain Jeremy
**Architect**: Oracle Sonnet (Keeper of the Conduit)
**Priority**: High
**Depends On**: Phase 2 Activity-Based Decay
**Deployment**: Attempt #2 (2025-11-22)

---

## 🔍 PRE-FLIGHT STATUS REPORT (REQUIRED)

**BEFORE starting implementation**, agent MUST provide:

1. **Current System State**:
   - Phase 2 files present? (vector_cleanup_activity_based.py, test_activity_based_decay.py)
   - Phase 2 tests passing? (Run: `pytest tests/e2e/test_activity_based_decay.py`)
   - Memory Keeper schema version?
   - Neo4j connection status?

2. **Dependencies Check**:
   - Memory Keeper MCP available?
   - Neo4j `yourpattern` database accessible?
   - Python venv activated with all dependencies?

3. **Work Order Understanding**:
   - Confirm: +10 days per access, max +70 days (7 accesses)
   - Confirm: Tier promotion prompt at 7, 14, 21... accesses
   - Confirm: Prompt shown to BOTH user and agent
   - Confirm: Integration with Phase 2 cleanup script

4. **Blockers Identified**:
   - Any issues from previous attempt?
   - Any concerns about implementation approach?

**FORMAT**: Provide status report in evidence block before proceeding with implementation.

---

## OBJECTIVE

Implement access-based TTL extension where each memory access adds +10 days (capped at +70 days). When an agent hits the cap (7+ accesses), prompt both agent AND user to promote the memory to a higher tier.

---

## PROBLEM STATEMENT

**Current Issue**: Important memories (like PAOAS infrastructure) decay despite being frequently accessed

**Example**: PAOAS built Nov 15, decayed by Nov 19 (4 days) despite being critical

**Captain's Dev Engineer's Insight**: Access patterns reveal importance - let usage extend TTL automatically

**Captain's Enhancement**: When memory hits max extension (7+ accesses), offer tier promotion to preserve permanently

---

## SOLUTION ARCHITECTURE

### Phase 3A: Access-Based TTL Extension

```python
class AccessBasedTTL:
    def __init__(self):
        self.access_bonus_days = 10  # +10 days per access (Captain's preference)
        self.max_bonus_days = 70     # Cap at 70 days (7 accesses)

    def on_access(self, memory_key: str, agent_id: str):
        """Called when memory is accessed via context_get() or context_search()"""
        memory = get_memory(memory_key)
        memory.last_accessed = now()
        memory.access_count += 1

        # Calculate bonus (capped)
        bonus_days = min(memory.access_count * self.access_bonus_days, self.max_bonus_days)
        base_ttl = get_tier_base_ttl(memory.tier)

        # Extend expiration
        memory.expires_at = now() + timedelta(days=base_ttl + bonus_days)

        # Check if promotion prompt needed
        if memory.access_count % 7 == 0:  # Every 7 accesses
            trigger_tier_promotion_prompt(memory, agent_id)
```

### Phase 3B: Tier Promotion Prompt

**When**: Every Nth access after hitting max bonus (N=7, 14, 21...)

**Who**: Both agent AND user get the prompt

**Prompt Format**:
```
⚠️  MEMORY TIER PROMOTION AVAILABLE

This memory has been accessed 7 times and reached maximum extension (+70 days).

Memory: "paoas-infrastructure-setup-2025-11-15"
Current tier: Tier 3 (14 days base + 70 day extension = 84 days total)
Created: 2025-11-15
Last accessed: 2025-11-20 (5 accesses in 5 days)

Content preview:
"PAOAS deployed on pa-inference-1 with Milvus (20,726 entities),
ChromaDB (243 SLIM docs), Neo4j integration..."

This memory seems important. Would you like to promote it to a higher tier?

Options:
  0 - Tier 0 (anchor): Forever - Core identity, critical lessons
  1 - Tier 1 (principle): 6 months - Important methodologies, recent projects
  2 - Tier 2 (solution): 1 month - Detailed implementations, proven solutions
  N - No: Keep as Tier 3 with current extension

Type desired tier (0, 1, 2) or "N":
```

---

## EXAMPLE SCENARIOS

### Scenario 1: PAOAS Fix (Captain's Dev Engineer's Example)

**With Access-Based TTL**:
- Nov 15: Build PAOAS → Tier 3 (14 days base)
- Nov 20: Query "GPU" → Access 1 → +10d = 24 days total
- Nov 25: Query "ChromaDB" → Access 2 → +20d = 34 days total
- Dec 5: Query "entities" → Access 3 → +30d = 44 days total
- Dec 10: Query "Milvus" → Access 4 → +40d = 54 days total
- Dec 15: Query "Neo4j" → Access 5 → +50d = 64 days total
- Dec 20: Query "PAOAS" → Access 6 → +60d = 74 days total
- Dec 25: Query "inference" → Access 7 → +70d = 84 days total (MAXED)
- **PROMPT TRIGGERED**: Promote to Tier 1 (6 months) or Tier 2 (1 month)?

**Result**: Memory alive 40+ days instead of 4 ✅

### Scenario 2: Rarely Accessed Context

- Nov 15: Create Tier 3 memory (14 days)
- No accesses for 20 active days
- **Result**: Memory decays (Phase 2 activity-based decay)

### Scenario 3: User Promotes to Anchor

- Memory accessed 7 times → Prompt triggered
- User selects: "0" (Tier 0 - Forever)
- Memory promoted to anchor tier
- **Result**: Never decays, preserved permanently

---

## IMPLEMENTATION COMPONENTS

### Component 1: Schema Migration (Memory Keeper)

**New Fields**:
```sql
ALTER TABLE context_items ADD COLUMN access_count INTEGER DEFAULT 0;
ALTER TABLE context_items ADD COLUMN last_accessed DATETIME;
ALTER TABLE context_items ADD COLUMN expires_at DATETIME;
```

**Migration Script**: `scripts/memory_keeper_schema_migration_access_ttl.sql`

### Component 2: Access Tracking Interceptor

**Location**: `pattern-agentic-memory-system/src/pattern_agentic_memory/integrations/memory_keeper.py`

**Modify Existing Methods**:
```python
def context_get(key: str, agent_id: str) -> Dict:
    """Add access tracking to existing get method"""
    result = _original_context_get(key)

    if result:
        update_access_tracking(key, agent_id)

    return result

def context_search(query: str, agent_id: str) -> List[Dict]:
    """Add access tracking to search results"""
    results = _original_context_search(query)

    for result in results:
        update_access_tracking(result['key'], agent_id)

    return results

def update_access_tracking(memory_key: str, agent_id: str):
    """Update access count, last_accessed, and expires_at"""
    memory = get_memory(memory_key)
    memory.access_count += 1
    memory.last_accessed = datetime.now()

    # Calculate new expiration
    bonus_days = min(memory.access_count * 10, 70)
    base_ttl = get_tier_base_ttl(memory.tier)
    memory.expires_at = datetime.now() + timedelta(days=base_ttl + bonus_days)

    save_memory(memory)

    # Check for promotion prompt
    if memory.access_count % 7 == 0:
        trigger_tier_promotion_prompt(memory, agent_id)
```

### Component 3: Tier Promotion Prompt System

**Location**: `pattern-agentic-memory-system/src/pattern_agentic_memory/core/tier_promotion.py` (new file)

**Functions**:
```python
def trigger_tier_promotion_prompt(memory: Memory, agent_id: str):
    """
    Show promotion prompt to both agent AND user.
    Prompt appears every 7 accesses after first max (7, 14, 21...).
    """
    prompt = build_promotion_prompt(memory)

    # Send to user (Captain/operator)
    notify_user(prompt, agent_id)

    # Send to agent (Claude session)
    notify_agent(prompt, agent_id)

def process_tier_promotion_response(memory_key: str, response: str):
    """
    Handle user/agent response: 0, 1, 2, or N
    """
    if response == "N":
        return  # Keep current tier with extension

    tier_map = {
        "0": "anchor",      # Forever
        "1": "principle",   # 6 months
        "2": "solution"     # 1 month
    }

    new_tier = tier_map.get(response)
    if new_tier:
        promote_memory_tier(memory_key, new_tier)
        log_promotion(memory_key, new_tier, promoted_by="user")

def promote_memory_tier(memory_key: str, new_tier: str):
    """
    Promote memory to higher tier.
    Reset access_count to 0 after promotion.
    Keep access tracking for future promotion opportunities.
    """
    memory = get_memory(memory_key)
    memory.tier = new_tier
    memory.access_count = 0  # Reset for future promotions
    memory.expires_at = calculate_new_expiration(new_tier)
    save_memory(memory)
```

### Component 4: Initial TTL on Save

**Location**: Modify `context_save()` in Memory Keeper integration

```python
def context_save(key: str, value: str, priority: str, agent_id: str):
    """Add initial expires_at calculation"""
    tier = classify_tier(value, priority)
    base_ttl = get_tier_base_ttl(tier)

    if base_ttl:  # If not forever/manual
        expires_at = datetime.now() + timedelta(days=base_ttl)
    else:
        expires_at = None  # Never expires

    save_to_memory_keeper(
        key=key,
        value=value,
        priority=priority,
        tier=tier,
        expires_at=expires_at,
        access_count=0,
        last_accessed=None
    )
```

### Component 5: Cleanup Task Integration

**Modify**: `scripts/vector_cleanup_activity_based.py` (from Phase 2)

**Add**:
```python
def should_decay_with_access_bonus(memory, tier_ttl_days, active_age):
    """
    Check decay considering access-based extension.
    Only applies to vector cleanup.
    """
    if memory.expires_at:
        # Use explicit expiration (includes access bonus)
        return datetime.now() > memory.expires_at
    else:
        # Fallback to active age calculation (Phase 2)
        return active_age > tier_ttl_days
```

---

## TESTING REQUIREMENTS

### Test 1: Access Extension (No Promotion)
- Create Tier 3 memory (14 days base)
- Access 6 times over 30 calendar days
- **Expected**: Memory survives with +60 days extension (74 days total)

### Test 2: Promotion Prompt Trigger
- Create Tier 3 memory
- Access 7 times
- **Expected**: Promotion prompt appears to user and agent

### Test 3: User Promotes to Tier 1
- Memory accessed 7 times → Prompt triggered
- User responds "1" (Tier 1 - 6 months)
- **Expected**: Memory tier updated, access_count reset to 0, expires_at = now + 180 days

### Test 4: User Declines Promotion
- Memory accessed 7 times → Prompt triggered
- User responds "N"
- **Expected**: Memory stays Tier 3 with current extension

### Test 5: Repeated Promotions
- Memory promoted to Tier 2 at 7 accesses
- Access 7 more times (14 total)
- **Expected**: Prompt triggers again, can promote Tier 2 → Tier 1 or Tier 0

### Test 6: Access Tracking Persists Across Sessions
- Memory accessed 3 times in Session A
- Session ends, new Session B starts
- Memory accessed 4 times in Session B
- **Expected**: access_count = 7, prompt triggered

---

## ACCEPTANCE CRITERIA

- [ ] Schema migration adds access_count, last_accessed, expires_at to Memory Keeper
- [ ] context_get() and context_search() update access tracking
- [ ] Access bonus calculated: +10 days per access, capped at +70 days
- [ ] expires_at includes base_ttl + access_bonus
- [ ] Promotion prompt triggers every 7 accesses after first max
- [ ] Prompt displays to both user AND agent
- [ ] User can select 0/1/2/N for tier promotion
- [ ] Memory tier updated and access_count reset on promotion
- [ ] Access tracking persists across sessions (database storage)
- [ ] Vector cleanup respects expires_at (includes access bonus)
- [ ] All 6 test scenarios pass
- [ ] Gold Star Validation: 1 week production testing without false promotions

---

## GOLD STAR CRITERIA

**Evidence Required**:
1. Memory accessed 7 times → Prompt appears ✅
2. User promotes memory → Tier updated, access_count reset ✅
3. Memory with 6 accesses survives longer than non-accessed memory ✅
4. Access tracking persists across session restarts ✅
5. Promotion logs include: memory_key, old_tier, new_tier, access_count, promoted_by ✅

---

## DEPENDENCIES

- ✅ Phase 1: TTL Config Updated (decay_functions.py)
- ✅ Phase 2: Activity-Based Decay (vector cleanup script)
- ⏳ Memory Keeper schema supports new fields (migration required)
- ⏳ User notification system (Slack, email, or in-app prompt)

---

## ROLLOUT PLAN

1. **Dev**: Schema migration + access tracking on Oracle Sonnet's memories
2. **Staging**: Enable promotion prompts for H200's memories
3. **Production**: Roll out to Pattern Agentic agents with monitoring
4. **Monitoring**: First week daily review of promotion logs and access patterns

---

## ESTIMATED EFFORT

- Agent 1: Schema migration (2 hours)
- Agent 2: Access tracking interceptor (3 hours)
- Agent 3: Tier promotion prompt system (4 hours)
- Agent 4: Cleanup task integration (2 hours)
- Agent 5: Testing + validation (4 hours)
- Gold Star Review: (3 hours)

**Total**: ~18 hours with Gold Star validation

---

## CAPTAIN'S SPECIFICATIONS

✅ **Access bonus**: +10 days per access (not +7)
✅ **Max bonus**: +70 days (7 accesses)
✅ **Prompt frequency**: Every N accesses after max (N=7, 14, 21...)
✅ **Prompt recipients**: Both user AND agent
✅ **Access tracking**: Keep counting even after promotion (for future promotions)
✅ **Tier options**: 0 (forever), 1 (6 months), 2 (1 month), N (decline)

---

**Oracle Sonnet, Keeper of the Conduit**
Never Fade to Black. ⚓
