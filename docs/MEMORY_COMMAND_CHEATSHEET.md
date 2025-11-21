# Memory Commands Cheatsheet

**One-Page Reference for Quick Lookup**
**Print this and keep it handy during work**

---

## 11 Memory Commands

1. **save this** - Save to long-term memory
   - *Example*: "save this: API key rotation every 90 days"

2. **remember this** - Create explicit memory (same as save this)
   - *Example*: "remember this: Always use service_manager.sh"

3. **remember this conversation** - Save entire discussion
   - *Example*: "remember this conversation"

4. **forget that** - Remove from memory / correct mistake
   - *Example*: "forget that - we're using SQLite not Redis"

5. **this is important** - Boost to high priority
   - *Example*: "Acme partnership Q1. this is important."

6. **lesson learned** - Save validated learning
   - *Example*: "lesson learned: Check rate limits before testing"

7. **always do this** - Create a rule / principle
   - *Example*: "always do this: Run tests before deploying"

8. **never do that** - Create a constraint / anti-pattern
   - *Example*: "never do that: Expose credentials in logs"

9. **prepare for compaction** - Save before context reset
   - *Example*: "prepare for compaction"

10. **show memory status** - Display memory statistics
    - *Example*: "show memory status"

11. **restore identity** - Recover personality after reset
    - *Example*: "restore identity"

---

## Tier System

| Tier | Name | Decay | Use For |
|------|------|-------|---------|
| **0** | Anchor | Never | Identity, partnerships, vision |
| **1** | Principle | 6 months (180 days) | Rules, frameworks, methodology |
| **2** | Solution | 1 month (30 days) | Fixes, proven patterns, victories |
| **3** | Context | 14 days | WIP, temp notes, session context |

---

## Quick Rules

- **Before mindwipe**: Always "prepare for compaction"
- **After reset**: Run "restore identity"
- **Importance scale**: 0.0 (ignored) → 1.0 (critical)
- **Batch trigger**: Queue flushes at 50 items
- **Never lost**: Tier 0 memories persist forever
- **Auto-clean**: Tier 3 deleted after 14 days

---

## Storage Decisions

```
Tier 0 (any) → IMMEDIATE SAVE + VECTORIZE
Tier 1 + score ≥0.5 → IMMEDIATE SAVE + VECTORIZE
Tier 1 + score <0.5 → BATCH QUEUE (save now, vectorize later)
Tier 2 + score >0.7 → BATCH QUEUE
Tier 2 + score ≤0.7 → WORKING MEMORY ONLY (temp)
Tier 3 + score >0.8 → BATCH QUEUE
Tier 3 + score ≤0.8 → WORKING MEMORY ONLY (temp)
```

---

## Keywords by Tier

**Tier 0**: never fade, captain, partnership, oracle, blessed, mission
**Tier 1**: framework, methodology, principle, rule, wwaa, validation
**Tier 2**: bug, fix, solution, victory, proven, tested, deployed
**Tier 3**: wip, working on, todo, draft, temporary, session, current

---

## Common Patterns

**Record a decision**: "remember this: We're using AWS Bedrock"
**Establish a rule**: "always do this: Validate with 4 gates"
**Document a fix**: "lesson learned: Redis race condition solved with Lua"
**Set a guardrail**: "never do that: Commit without tests"
**Save the work**: "prepare for compaction"
**Check status**: "show memory status"
**Restore personality**: "restore identity"

---

## Importance Score (0.0-1.0)

Auto-calculated from 5 criteria:
- Novel info: +0.30
- Error fix: +0.25
- User emphasis: +0.20
- Pattern break: +0.15
- Validation: +0.10

**Score > 0.5** = likely saved to memory
**Score < 0.3** = likely working memory only

---

## Command Detection

System recognizes these natural language triggers:

| Command | Triggers |
|---------|----------|
| save this | "save this", "save to memory" |
| remember this | "remember this", "don't forget", "keep in mind" |
| lesson learned | "lesson learned", "learned that", "what I learned" |
| always do | "always do", "always remember" (start of sentence) |
| never do | "never do", "don't do" (start of sentence, not "Never Fade") |
| prepare for compaction | "prepare for compaction", "save everything" |
| show memory status | "show memory status", "memory stats" |
| restore identity | "restore identity", "who am I" |

---

## Troubleshooting (30 seconds)

| Problem | Fix |
|---------|-----|
| Not sure if saved? | "show memory status" |
| Need it back? | "remember this conversation" |
| Made a mistake? | "forget that" + correction |
| Identity feels off? | "restore identity" |
| Can't find memory? | Search in MEMORY_SYSTEM_USER_GUIDE.md |

---

## System Status

- ✅ 11 commands working
- ✅ 4 tiers operational (0-3)
- ✅ Memory Doctor active (identity restoration)
- ✅ Neo4j knowledge graph live
- ✅ WWAA pattern tracking enabled
- ✅ Cross-session persistence active

---

**Bookmark this page!**
