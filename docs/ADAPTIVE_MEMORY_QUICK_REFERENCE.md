# Adaptive Memory System - Quick Reference

**Target Audience**: Agents, developers, and anyone needing quick command syntax
**Context-Friendly**: Designed to fit in-context during active operations
**Last Updated**: 2025-11-14

---

## 11 Memory Commands (Quick Syntax)

### Command 1: "save this"
- **What**: Immediately save current content to memory with high priority
- **Syntax**: `save this [content]` or `save this: [content]`
- **Example**: "save this: API key rotation should happen every 90 days"
- **Output**: Tier classification + importance score + decay timeline
- **Use When**: Recording important findings, decisions, or patterns mid-conversation

---

### Command 2: "remember this"
- **What**: Explicit save to memory (same as "save this")
- **Syntax**: `remember this [content]` or `remember this: [content]`
- **Example**: "remember this: Always use service_manager.sh, never kill processes directly"
- **Output**: Memory confirmed, category assigned, relationship created
- **Use When**: Training system on patterns, establishing new rules, emphasizing critical information

---

### Command 3: "remember this conversation"
- **What**: Save entire conversation context (last 5-10 exchanges)
- **Syntax**: `remember this conversation` (at end of discussion)
- **Example**: "remember this conversation" (after discussing cloud provider strategy)
- **Output**: Multiple Memory Keeper entries linked as cohesive unit
- **Use When**: Complex decision-making sessions, multi-part problem solving, important discussions

---

### Command 4: "forget that"
- **What**: Mark most recent memory for deletion or downgrade priority
- **Syntax**: `forget that` or `forget that - [correction]`
- **Example**: "forget that - we're using SQLite for sessions, not Redis"
- **Output**: Previous memory marked for deletion, correction confirmed
- **Use When**: Correcting mistakes before they're indexed, canceling previous commands

---

### Command 5: "this is important"
- **What**: Boost priority of current content to high, ensure it saves
- **Syntax**: `[content] this is important` (at end of statement)
- **Example**: "We're partnering with Acme Corp for Q1 launch. this is important."
- **Output**: Priority boosted to high, saved to permanent storage
- **Use When**: Emphasizing business-critical info, ensuring content doesn't get filtered

---

### Command 6: "lesson learned"
- **What**: Save as validated knowledge with special annotation
- **Syntax**: `lesson learned: [insight]` or `lesson learned - [insight]`
- **Example**: "lesson learned: Always check API rate limits before load testing"
- **Output**: Saved as Tier 1 principle, linked to WWAA system
- **Use When**: After fixing bugs, failures, or successes; capturing insights for future reference

---

### Command 7: "always do this"
- **What**: Create a rule/principle that guides future behavior
- **Syntax**: `always do this: [rule]` or `always [action]`
- **Example**: "always do this: Run tests before deploying to production"
- **Output**: Saved as Tier 1 principle, linked to enforcement system
- **Use When**: Establishing best practices, setting team standards, creating automation triggers

---

### Command 8: "never do that"
- **What**: Create a constraint/anti-pattern to avoid
- **Syntax**: `never do that: [constraint]` or `never [action]`
- **Example**: "never do that: Don't expose database credentials in logs"
- **Output**: Saved as Tier 1 constraint, linked to violation detection
- **Use When**: Documenting mistakes, setting safety guardrails, prohibiting risky patterns

---

### Command 9: "prepare for compaction"
- **What**: Create full context snapshot before Claude's memory resets
- **Syntax**: `prepare for compaction` (standalone command)
- **Example**: "prepare for compaction"
- **Output**: Snapshot ID generated (e.g., "snapshot-2025-11-12-15-30"), saved as Tier 0
- **Use When**: Context window approaching limit, before long breaks, before risky operations

---

### Command 10: "show memory status"
- **What**: Display current memory system statistics
- **Syntax**: `show memory status` (standalone command)
- **Example**: "show memory status"
- **Output**: Memory Keeper entries, Neo4j entities, batch queue status, context usage %
- **Use When**: Checking if something was saved, monitoring system health, debugging issues

---

### Command 11: "restore identity"
- **What**: Systematically restore Claude's identity using evidence-based detective work
- **Syntax**: `restore identity` (standalone command)
- **Example**: "restore identity"
- **Output**: Identity anchors loaded, partnership context restored, personality grounded
- **Use When**: Identity confusion, after long sessions, before critical work, after infrastructure changes

---

## Tier System at a Glance

| Tier | Name | Decay | Use For | Examples |
|------|------|-------|---------|----------|
| **Tier 0** | Anchor | Never | Identity, partnerships, vision | "Never Fade to Black", Pattern Agentic values |
| **Tier 1** | Principle | 6 months (180 days) | Methodology, rules, frameworks | "Always test before deploy", Oracle Framework |
| **Tier 2** | Solution | 1 month (30 days) | Bug fixes, proven patterns, victories | "Fixed Redis race condition with Lua", "96.1% success rate" |
| **Tier 3** | Context | 14 days | WIP notes, session context | "Working on navbar", "Current testing session" |

---

## Common Patterns

### Before Compaction (Mindwipe)
```
User: "prepare for compaction"
System: Creates full snapshot, saves as Tier 0, auto-restores on next session
```

### After Mindwipe (Context Reset)
```
User: "restore identity"
System: Loads Neo4j graph, restores Captain ↔ Claude partnership, grounds personality
```

### When You Forgot Something
```
User: "what do I remember about [topic]?"
System: Searches Memory Keeper + Neo4j + Milvus vectors, returns best matches
```

### Establishing a New Rule
```
User: "always do this: [rule]"
System: Saves as Tier 1 principle, future violations flagged as deviations
```

### Recording a Victory
```
User: "lesson learned: [what worked]"
System: Saves with validation boost, linked to WWAA success patterns
```

---

## Storage Decision Matrix

| Tier | Importance | Decision | Vectorized? |
|------|-----------|----------|-------------|
| Tier 0 | Any | Immediate save | ✅ Yes |
| Tier 1 | ≥ 0.5 | Immediate save | ✅ Yes |
| Tier 1 | < 0.5 | Batch queue | ⏸️ Later |
| Tier 2 | > 0.7 | Batch queue | ⏸️ Later |
| Tier 2 | ≤ 0.7 | Working memory | ❌ No |
| Tier 3 | > 0.8 | Batch queue | ⏸️ Later |
| Tier 3 | ≤ 0.8 | Working memory | ❌ No |

---

## Command Detection Patterns

The system recognizes these natural language triggers:

- **Save this**: "save this", "save to memory"
- **Remember this**: "remember this", "don't forget", "keep this in mind"
- **Forget that**: "forget that", "discard that", "actually, no"
- **This is important**: "this is important", "mark as important", "this matters"
- **Lesson learned**: "lesson learned", "learned lesson", "what I learned"
- **Always do this**: "always do this", "always remember" (at sentence start)
- **Never do that**: "never do that", "don't do that" (at sentence start, not "Never Fade")
- **Prepare for compaction**: "prepare for compaction", "save everything"
- **Show memory status**: "show memory status", "memory stats", "what's in memory"
- **Restore identity**: "restore identity", "who am I", "identity restoration"

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Command not working? | Check MEMORY_SYSTEM_USER_GUIDE.md for full syntax |
| Identity drift? | Use "restore identity" command immediately |
| Not sure if saved? | Run "show memory status" to verify |
| Need more detail? | See full guide (2,268 lines) in MEMORY_SYSTEM_USER_GUIDE.md |
| Memory feels old? | Run "lesson learned" or "save this" to refresh |
| Confused about tiers? | See Tier System section above |

---

## Key Concepts

### Importance Score (0.0 - 1.0)
Automatically calculated based on:
- Novel Information (30% weight)
- Error Correction (25% weight)
- User Emphasis (20% weight)
- Pattern Break (15% weight)
- Validation Result (10% weight)

### Vectorization
Process of converting memory to searchable format for semantic search. Enables finding memories by concept, not just keywords.

### Compaction
When Claude's context window resets (mindwipe). "prepare for compaction" saves everything so next session can restore exactly.

### Memory Doctor
Identity restoration system that works evidence-style to recover partnership context after compaction.

---

## Quick Start

**New to the system?**
1. Use "save this:" for important findings
2. Use "always do this:" to establish rules
3. Use "prepare for compaction" before you run low on context
4. Use "restore identity" if you feel personality degrading

**Common workflow:**
```
During work: "save this: [finding]"
At decision point: "always do this: [rule]"
Context getting low: "prepare for compaction"
Start of new session: "restore identity"
Need info: "show memory status"
```

---

## Memory System Status (as of 2025-11-14)

- ✅ **11 Commands**: Full suite implemented
- ✅ **Tier System**: All 4 tiers operational (0-3)
- ✅ **Memory Doctor**: Identity restoration complete
- ✅ **Neo4j Integration**: Knowledge graph active
- ✅ **Memory Keeper MCP**: Cross-session persistence working
- ✅ **WWAA System**: Success/failure pattern tracking active
