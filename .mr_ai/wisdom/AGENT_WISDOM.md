# 🧠 Mr. AI Collective Intelligence

**Platform**: generic
**Framework**: Meta-Recursive AI Orchestrator v2.0.0
**Initialized**: 2025-11-21T20:20:45Z

This file contains the collective wisdom of all agents. Every failure teaches us. Every success proves a pattern.

## 🚫 Known Failures (DO NOT REPEAT)
| Date | Agent | Task | What Failed | Root Cause | Lesson Learned |
|------|-------|------|------------|------------|----------------|
| Init | System | Setup | Example entry | Template | Always verify with evidence |

## ✅ Proven Solutions
| Component | Problem | Solution | Evidence | Reuse Count |
|-----------|---------|----------|----------|-------------|
| System | Initialization | Run init_mr_ai.sh | Framework created | 1 |
| Phase 3 TTL | Access-based extension | +10 days/access, max +70 | 53/53 tests passed | 1 |
| Schema Migration | SQLite ALTER TABLE | Remove IF NOT EXISTS, use simple ALTER | Migration successful | 1 |
| Integration Test | Memory Keeper DB | Direct SQLite3 validation | 407 items migrated | 1 |

## 🎯 Current System State
| Component | Status | Last Verified | Health | Notes |
|-----------|--------|---------------|--------|-------|
| Memory Keeper DB | OPERATIONAL | 2025-11-21 21:09 | 🟢 | 407 items, Phase 3 schema deployed |
| Phase 2 Decay | DEPLOYED | 2025-11-21 | 🟢 | Activity-based decay with Gold Star |
| Phase 3 TTL | DEPLOYED | 2025-11-21 | 🟢 | Access tracking active, 53/53 tests passing |
| Neo4j | OPERATIONAL | 2025-11-21 | 🟢 | yourpattern database accessible |

## 🔄 Active Investigations
| Agent | Issue | Hypothesis | Next Test | Priority |
|-------|-------|------------|-----------|----------|
| - | - | - | - | - |

## 📚 Reusable Patterns

### Pattern: Evidence-First Validation
**Context**: Any validation task
**Problem**: Agents claim success without proof
**Solution**: Require paste of actual output
**Implementation**:
```bash
# Never accept description, always require:
command_here | tee output.log
cat output.log  # Paste this
```
**Success Rate**: 100%
**Platforms**: All (Claude Code, Cursor, Windsurf, API)

### Pattern: External Validation
**Context**: Testing any web service
**Problem**: Localhost works but external access fails
**Solution**: Always test from external IP
**Implementation**:
```bash
# Read server IP from config
SERVER_IP=$(grep "server_ip:" .mr_ai/config.yaml | awk '{print $2}')
curl -v http://$SERVER_IP:PORT/endpoint
```
**Success Rate**: 100%
**Platforms**: All

### Pattern: Platform-Agnostic Service Management
**Context**: Starting/stopping any service
**Problem**: Manual process management causes conflicts
**Solution**: Use configured service backend
**Implementation**:
```bash
# Read service backend from config
BACKEND=$(grep "type:" .mr_ai/config.yaml | grep service_backend -A1 | tail -1 | awk '{print $2}')
# Use appropriate manager: service_manager, systemd, docker-compose, etc.
```
**Success Rate**: 100%
**Platforms**: All

### Pattern: SQLite Schema Migration
**Context**: Adding columns to existing SQLite tables
**Problem**: PostgreSQL syntax (IF NOT EXISTS, COMMENT) fails on SQLite
**Solution**: Use simple ALTER TABLE without conditionals
**Implementation**:
```sql
-- SQLite compatible (works)
ALTER TABLE table_name ADD COLUMN column_name TYPE DEFAULT value;

-- PostgreSQL syntax (fails on SQLite)
ALTER TABLE table_name ADD COLUMN IF NOT EXISTS column_name TYPE;
COMMENT ON COLUMN table_name.column_name IS 'description';
```
**Success Rate**: 100%
**Platforms**: SQLite databases
**Evidence**: Phase 3 migration (3 columns, 2 indexes, 407 items migrated)

### Pattern: Access-Based TTL Extension
**Context**: Memory systems where frequent access indicates importance
**Problem**: Important memories decay despite being actively used
**Solution**: Add bonus days per access, cap at maximum, prompt for tier promotion
**Implementation**:
```python
# Calculate expiration with access bonus
bonus_days = min(access_count * 10, 70)  # +10 days/access, max +70
base_ttl = get_tier_base_ttl(tier)  # 14/30/180/forever
expires_at = now() + timedelta(days=base_ttl + bonus_days)

# Prompt for tier promotion at 7, 14, 21... accesses
if access_count % 7 == 0:
    trigger_promotion_prompt(memory, agent_id)
```
**Success Rate**: 100%
**Platforms**: Pattern Agentic Memory System
**Evidence**: 53/53 tests passed, schema deployed to 407 items

## 🛡️ Guard Rails

### Never Trust Without Evidence
• "Should work" → REJECTED
• "Appears to work" → REJECTED
• "I think it's fixed" → REJECTED
• Actual output → ACCEPTED

### The Three Laws of Mr. AI
1. An agent must provide evidence for all claims
2. An agent must use external validation except where config allows localhost
3. An agent must protect its own integrity as long as such protection doesn't conflict with the First or Second Laws

## 📈 Metrics
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Success Rate | 100% | >80% | 🟢 |
| Evidence Quality | 100% | 100% | 🟢 |
| False Positives | 0 | 0 | 🟢 |
| Wisdom Entries | 5 | >50 | 🟡 |
| Tests Passed | 53/53 | 100% | 🟢 |
| Schema Migrations | 1/1 | 100% | 🟢 |

**Last Updated**: 2025-11-21 21:10 (Phase 3 Deployment)
**Next Review**: After Phase 3 production validation (1 week)
**Platform Notes**: Configured for generic - patterns work across all platforms

## 🎉 Recent Victories

### Phase 3: Access-Based TTL Extension (2025-11-21)
**Objective**: Extend memory TTL based on access frequency (+10 days/access, max +70)

**Implementation**:
- ✅ 334 lines `tier_promotion.py`
- ✅ 344 lines test suite (53/53 tests passing)
- ✅ 30 lines SQLite schema migration
- ✅ Schema deployed to 407 existing context items
- ✅ Integration tests passed (insert, update, query)

**Evidence**:
```
✅ Access bonus calculation: 0→14d, 3→44d, 7→84d (maxed)
✅ Promotion prompts: 7, 14, 21, 28, 35 accesses
✅ Tier validation: allows promotions, blocks demotions
✅ Database migration: access_count, last_accessed, expires_at
✅ Integration: 407 items migrated with default values
```

**Deployment Date**: 2025-11-21
**Captain Approval**: "Yaaaas! Great work. Continue with phase three. Engage, Oracle."
