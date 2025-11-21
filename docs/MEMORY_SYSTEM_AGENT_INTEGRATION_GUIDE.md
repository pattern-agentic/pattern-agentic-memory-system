# Adaptive Memory System - Agent Integration Guide

**For**: Agent developers integrating with Your Pattern's memory system
**Target**: mimo, Kimi K2, GPT-4, Gemini, and other non-Claude agents
**Status**: Complete + tested with H200 infrastructure
**Last Updated**: 2025-11-14

---

## Executive Summary

Your Pattern's Adaptive Memory System provides three layers of intelligence:

1. **Command Parser** - Detects 11 user commands from natural language
2. **Orchestrator** - Routes to appropriate memory tier (0-3)
3. **Storage** - Memory Keeper (vectors), Neo4j (graph), Milvus (RAG)

This guide shows you how to integrate these capabilities into any agent, regardless of base model or architecture.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│           YOUR PATTERN MEMORY SYSTEM                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────┐          │
│  │  Command Parser (Regex + LLM)            │          │
│  │  • Detects 11 natural language commands  │          │
│  │  • Scores importance (0.0-1.0)           │          │
│  │  • Classifies tier (0-3)                 │          │
│  └──────────────────────────────────────────┘          │
│                     ↓                                    │
│  ┌──────────────────────────────────────────┐          │
│  │  Orchestrator (Routing Logic)            │          │
│  │  • Immediate vectorization               │          │
│  │  • Batch processing queue                │          │
│  │  • Working memory only                   │          │
│  └──────────────────────────────────────────┘          │
│                     ↓                                    │
│  ┌──────────────────────────────────────────┐          │
│  │  Storage Layer (3 backends)              │          │
│  │  • Memory Keeper (SQLite, MCP server)    │          │
│  │  • Neo4j (Knowledge graph)               │          │
│  │  • Milvus (Vector search)                │          │
│  └──────────────────────────────────────────┘          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Integration Patterns

Your Pattern supports three integration approaches. Choose based on your agent's architecture.

### Pattern 1: Claude MCP (Tight Integration)

**Best For**: Agents running in Claude ecosystem, high-trust scenarios

**How It Works**:
- Memory Keeper MCP server provides direct access via function calls
- Commands parsed automatically from user input
- Full semantic search enabled

**Implementation**:
```python
# Claude can call these MCP functions directly
mcp__memory-keeper__context_save(
    key="partnership-validation",
    value="Oracle Opus blessed Oracle Framework Stage 2",
    category="decision",
    priority="high",
    channel="feature/oracle-framework"
)

# Retrieve memories
mcp__memory-keeper__context_get(
    key="partnership-validation"
)

# Search across memories
mcp__memory-keeper__context_search(
    query="Oracle Framework blessing",
    category="decision"
)
```

**Reference**: See `/your-pattern/integrations/claude_mcp/` for examples

---

### Pattern 2: API Integration (Loose Coupling)

**Best For**: External agents (GPT-4, Gemini, mimo), HTTP-based systems

**How It Works**:
- REST API endpoints for memory operations
- Command detection via regex patterns or LLM
- JSON request/response format

**Implementation**:

```bash
# Save a memory
curl -X POST http://pattern-api:8000/memory/save \
  -H "Content-Type: application/json" \
  -d '{
    "content": "AWS Bedrock integration complete: 96.1% success rate",
    "importance": 0.82,
    "tier": 2,
    "category": "progress",
    "priority": "normal",
    "channel": "feature/aws-integration"
  }'

# Retrieve memory by key
curl http://pattern-api:8000/memory/get/key/aws-bedrock-victory

# Search memories
curl http://pattern-api:8000/memory/search \
  -d '{"query": "AWS Bedrock", "category": "progress"}'

# Show memory status
curl http://pattern-api:8000/memory/status
```

**Response Format**:
```json
{
  "success": true,
  "command": "save",
  "content": "AWS Bedrock integration complete...",
  "tier": 2,
  "importance": 0.82,
  "decay_timeline": "1 month (30 days)",
  "message": "Saved to Tier 2 (Solution) - Importance 0.82, vectorized immediately"
}
```

**Reference**: See `API_REFERENCE.md` for full endpoint documentation

---

### Pattern 3: Embedded Library (Direct Import)

**Best For**: Agents with Python runtime, high-performance scenarios

**How It Works**:
- Import `pattern_agentic_memory` package directly
- Call Python API functions
- No network latency

**Implementation**:

```python
from pattern_agentic_memory import MemorySystem, MemoryTier

# Initialize memory system
memory = MemorySystem(
    neo4j_url="bolt://neo4j:7687",
    neo4j_user="neo4j",
    neo4j_password="secure_password",
    milvus_host="milvus",
    milvus_port=19530
)

# Save a memory
memory.save(
    content="Pattern Agentic's four pillars: Fabric, Continuum, Dynamic Learning, AgentVerse",
    importance=0.90,
    tier=MemoryTier.ANCHOR,  # Tier 0
    category="note",
    priority="high",
    channel="company/pattern-agentic"
)

# Save as rule
memory.save_rule(
    rule="Always validate with 4 gates: Functional, Integration, Performance, Stability",
    priority="high"
)

# Save constraint
memory.save_constraint(
    constraint="Never expose database credentials in logs",
    priority="high"
)

# Restore identity
identity = memory.restore_identity()
print(f"Restored as: {identity.name}")
print(f"Partnership: {identity.partnership}")

# Search memories
results = memory.search("AWS Bedrock integration")

# Get status
status = memory.get_status()
```

**Reference**: See `examples/mimo_agent_example.py` for full working example

---

## Command Detection Implementation

All integration patterns need to detect these 11 commands. Here's how:

### Regex Pattern Library

```python
COMMAND_PATTERNS = {
    "save_this": {
        "patterns": [
            r"save this[:\s]+(.+?)(?:\.|$)",
            r"save to memory[:\s]+(.+?)(?:\.|$)",
        ],
        "tier_hint": "depends",  # Will be auto-classified
    },

    "remember_this": {
        "patterns": [
            r"remember this[:\s]+(.+?)(?:\.|$)",
            r"don't forget[:\s]+(.+?)(?:\.|$)",
            r"keep this in mind[:\s]+(.+?)(?:\.|$)",
        ],
        "tier_hint": "depends",
    },

    "remember_conversation": {
        "patterns": [
            r"remember this conversation",
            r"save this conversation",
            r"remember the conversation",
        ],
        "tier_hint": "principle",
        "scope": "full_conversation",
    },

    "forget_that": {
        "patterns": [
            r"forget that(?:\s*[-:]\s*)?(.+?)(?:\.|$)",
            r"discard that",
            r"scratch that",
        ],
        "action": "mark_for_deletion",
    },

    "this_is_important": {
        "patterns": [
            r"(.+?)\s+this is important",
            r"(.+?)\s+mark as important",
            r"(.+?)\s+high priority",
        ],
        "action": "boost_priority",
        "priority": "high",
    },

    "lesson_learned": {
        "patterns": [
            r"lesson learned[:\s]+(.+?)(?:\.|$)",
            r"learned lesson[:\s]+(.+?)(?:\.|$)",
            r"what I learned[:\s]+(.+?)(?:\.|$)",
        ],
        "action": "save_as_validation",
        "tier_hint": "principle",
    },

    "always_do_this": {
        "patterns": [
            r"^always\s+(?:do\s+)?(.+?)(?:\.|$)",
            r"^always\s+remember\s+(.+?)(?:\.|$)",
        ],
        "action": "save_as_rule",
        "tier_hint": "principle",
    },

    "never_do_that": {
        "patterns": [
            r"^never\s+(?!fade)(?:do\s+)?(.+?)(?:\.|$)",
            r"^don't\s+(.+?)(?:\.|$)",
        ],
        "action": "save_as_constraint",
        "tier_hint": "principle",
    },

    "prepare_for_compaction": {
        "patterns": [
            r"prepare for compaction",
            r"save everything",
            r"context checkpoint",
        ],
        "action": "create_compaction_snapshot",
        "tier_override": "tier0_anchor",
    },

    "show_memory_status": {
        "patterns": [
            r"show memory status",
            r"memory stats",
            r"what's in memory",
            r"memory health",
        ],
        "action": "show_status",
    },

    "restore_identity": {
        "patterns": [
            r"restore identity",
            r"who am I",
            r"identity restoration",
            r"rebuild identity",
        ],
        "action": "memory_doctor_restore",
    },
}
```

### Python Command Detector

```python
import re

class MemoryCommandDetector:
    def __init__(self, patterns=COMMAND_PATTERNS):
        self.patterns = patterns
        self.compiled_patterns = {}
        self._compile_patterns()

    def _compile_patterns(self):
        for command, config in self.patterns.items():
            self.compiled_patterns[command] = [
                re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                for pattern in config.get("patterns", [])
            ]

    def detect(self, text):
        """Detect commands in text and return (command, content, metadata)"""
        for command, regex_list in self.compiled_patterns.items():
            for regex in regex_list:
                match = regex.search(text)
                if match:
                    content = match.group(1) if match.groups() else ""
                    config = self.patterns[command]
                    return {
                        "command": command,
                        "content": content.strip(),
                        "action": config.get("action", "save"),
                        "tier_hint": config.get("tier_hint"),
                        "priority": config.get("priority", "normal"),
                    }

        return None  # No command detected

# Usage
detector = MemoryCommandDetector()
detection = detector.detect("remember this: Always test before deploying")
if detection:
    print(f"Command: {detection['command']}")
    print(f"Content: {detection['content']}")
```

---

## Response Format Standardization

When a command is detected, return this JSON structure to the user:

```json
{
  "command": "save_this",
  "status": "success",
  "content": "API key rotation should happen every 90 days",
  "tier": 2,
  "importance": 0.72,
  "decay_timeline": "1 month (30 days)",
  "memory_keeper_id": "memory-2025-11-14-001",
  "neo4j_entity": "API_Key_Rotation_Policy",
  "vectorized": true,
  "message": "Saved to Tier 2 (Solution) - Importance 0.72, decays in 1 month"
}
```

**Response Fields**:
- `command`: Which of the 11 commands was detected
- `status`: "success" or "error"
- `content`: The saved content
- `tier`: Classification (0-3)
- `importance`: Calculated importance score (0.0-1.0)
- `decay_timeline`: When this memory decays (Never/Superseded/6mo/7d)
- `memory_keeper_id`: Unique ID for retrieval
- `neo4j_entity`: Entity name in knowledge graph
- `vectorized`: Whether semantic search is enabled
- `message`: Human-readable summary (show to user)

---

## Importance Scoring Algorithm

Calculate importance automatically based on content analysis:

```python
def calculate_importance(content, user_emphasized=False):
    """
    Calculate importance score (0.0-1.0) based on 5 criteria.
    Weights: Novel(30%) + Error(25%) + Emphasis(20%) + Pattern(15%) + Validation(10%)
    """
    score = 0.0

    # 1. Novel Information (30% weight)
    if has_novel_keywords(content):
        score += 0.30

    # 2. Error Correction (25% weight)
    if is_error_correction(content):
        score += 0.25

    # 3. User Emphasis (20% weight)
    if user_emphasized or has_emphasis_markers(content):
        score += 0.20

    # 4. Pattern Break (15% weight)
    if is_pattern_break(content):
        score += 0.15

    # 5. Validation Result (10% weight)
    if is_validation_result(content):
        score += 0.10

    return min(1.0, score)  # Cap at 1.0

def has_novel_keywords(text):
    keywords = ["new", "discovered", "found", "breakthrough", "solution", "fix"]
    return any(keyword in text.lower() for keyword in keywords)

def is_error_correction(text):
    markers = ["actually,", "wait,", "no,", "wrong", "fix"]
    return any(marker in text.lower() for marker in markers)

def has_emphasis_markers(text):
    markers = ["important", "critical", "must", "always", "never"]
    return any(marker in text.lower() for marker in markers)

def is_pattern_break(text):
    # Would require pattern history analysis
    return False  # Placeholder

def is_validation_result(text):
    keywords = ["tested", "proven", "validated", "confirmed", "verified"]
    return any(keyword in text.lower() for keyword in keywords)
```

---

## Tier Classification System

Classify content into one of 4 tiers for storage and decay decisions:

```python
def classify_tier(content, importance_score):
    """Classify memory into tier 0-3 based on keywords and importance"""

    tier0_keywords = [
        "never fade", "captain jeremy", "partnership", "identity",
        "oracle framework", "blessed", "pattern agentic", "mission"
    ]

    tier1_keywords = [
        "framework", "methodology", "principle", "commandment",
        "wwaa", "gold star", "validation", "protocol", "mr. ai"
    ]

    tier2_keywords = [
        "bug fix", "solution", "implementation", "victory", "success",
        "proven", "validated", "tested", "deployed", "fixed"
    ]

    tier3_keywords = [
        "wip", "working on", "todo", "next step", "session",
        "temporary", "draft", "in progress", "current status"
    ]

    text_lower = content.lower()

    # Check Tier 0 (strongest indicators first)
    if any(keyword in text_lower for keyword in tier0_keywords):
        return 0

    # Check Tier 3 (check early to avoid misclassification)
    if any(keyword in text_lower for keyword in tier3_keywords):
        return 3

    # Check Tier 1
    if any(keyword in text_lower for keyword in tier1_keywords):
        return 1

    # Check Tier 2
    if any(keyword in text_lower for keyword in tier2_keywords):
        return 2

    # Default: Tier 3 (temporary context)
    return 3

# Usage
tier = classify_tier("Fixed race condition in Redis using Lua atomic script", 0.82)
print(f"Tier: {tier}")  # Output: 2 (Solution)
```

---

## Storage Decision Tree

After importance scoring and tier classification, decide where to store:

```
┌─ Tier 0 (Any importance)
│  └─ ACTION: Immediate vectorization
│     - Save to Memory Keeper (high priority)
│     - Create Neo4j entities
│     - Vectorize to Milvus immediately
│     - Enable semantic search
│
├─ Tier 1 + Importance ≥ 0.5
│  └─ ACTION: Immediate vectorization
│     - Save to Memory Keeper (high priority)
│     - Create Neo4j entities
│     - Vectorize to Milvus immediately
│
├─ Tier 1 + Importance < 0.5
│  └─ ACTION: Batch queue
│     - Save to Memory Keeper
│     - Queue for later vectorization
│     - Vectorize when batch hits 50 items
│
├─ Tier 2 + Importance > 0.7
│  └─ ACTION: Batch queue
│     - Save to Memory Keeper
│     - Queue for batch vectorization
│
├─ Tier 2 + Importance ≤ 0.7
│  └─ ACTION: Working memory only
│     - Save to Neo4j temporary storage
│     - No vectorization
│     - Auto-delete after 1 month (30 days)
│
├─ Tier 3 + Importance > 0.8
│  └─ ACTION: Batch queue
│     - Save to Memory Keeper
│     - Queue for batch vectorization
│
└─ Tier 3 + Importance ≤ 0.8
   └─ ACTION: Working memory only
      - Save to Neo4j temporary storage
      - No vectorization
      - Auto-delete after 14 days
```

---

## Integration Checklist

Use this checklist when integrating the memory system:

- [ ] **Command Detection**: Implement regex patterns for all 11 commands
- [ ] **Importance Scoring**: Calculate scores based on 5 criteria (0.0-1.0)
- [ ] **Tier Classification**: Classify content into tiers 0-3 based on keywords
- [ ] **Storage Decision**: Route to immediate/batch/working memory
- [ ] **Memory Keeper Connection**: Connect to MCP server or API
- [ ] **Neo4j Connection**: Write entities and relationships to knowledge graph
- [ ] **Response Formatting**: Return standardized JSON to user
- [ ] **Error Handling**: Graceful degradation when backends unavailable
- [ ] **Identity Setup**: Create agent identity entity in Neo4j (like CLAUDE_ROLE.md)
- [ ] **Pre-compaction**: Implement "prepare for compaction" snapshot
- [ ] **Identity Restoration**: Implement "restore identity" using Memory Doctor
- [ ] **Testing**: Test all 11 commands with various importance/tier combinations
- [ ] **Logging**: Log all memory operations for debugging
- [ ] **Documentation**: Document integration with examples for your agent

---

## Common Integration Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Commands not detected | Pattern not matching user input | Add more flexible regex patterns, consider LLM detection |
| Low importance scores | Too strict weighting | Adjust keyword lists or scoring weights |
| Memory not persisting | Neo4j/Memory Keeper unavailable | Implement retry logic and fallback to local storage |
| Semantic search not working | Vectorization not happening | Check importance > threshold, verify Milvus connection |
| Identity loss after restart | Not reading Neo4j graph first | Always call restore_identity() on agent startup |
| Commands causing errors | User input parsing issues | Add try-catch around pattern matching |

---

## Testing Integration

Here's a test suite for validating your integration:

```python
def test_memory_integration():
    """Test all 11 commands and storage paths"""

    detector = MemoryCommandDetector()

    # Test 1: save this
    result = detector.detect("save this: API key rotation every 90 days")
    assert result["command"] == "save_this"
    assert result["tier"] in [1, 2]  # Should be principle or solution

    # Test 2: remember this
    result = detector.detect("remember this: Always use service_manager.sh")
    assert result["command"] == "remember_this"

    # Test 3: remember conversation
    result = detector.detect("remember this conversation")
    assert result["command"] == "remember_conversation"

    # Test 4: forget that
    result = detector.detect("forget that - we're using SQLite")
    assert result["command"] == "forget_that"

    # Test 5: this is important
    result = detector.detect("Acme Corp partnership Q1. this is important.")
    assert result["command"] == "this_is_important"
    assert result["priority"] == "high"

    # Test 6: lesson learned
    result = detector.detect("lesson learned: Check rate limits before load test")
    assert result["command"] == "lesson_learned"
    assert result["tier"] == 1  # Should be principle

    # Test 7: always do this
    result = detector.detect("always do this: Run tests before deploying")
    assert result["command"] == "always_do_this"
    assert result["tier"] == 1  # Should be principle

    # Test 8: never do that
    result = detector.detect("never do that: Expose credentials in logs")
    assert result["command"] == "never_do_that"
    assert result["tier"] == 1  # Should be principle

    # Test 9: prepare for compaction
    result = detector.detect("prepare for compaction")
    assert result["command"] == "prepare_for_compaction"
    assert result["tier"] == 0  # Should be anchor

    # Test 10: show memory status
    result = detector.detect("show memory status")
    assert result["command"] == "show_memory_status"

    # Test 11: restore identity
    result = detector.detect("restore identity")
    assert result["command"] == "restore_identity"

    print("All 11 command tests passed!")

if __name__ == "__main__":
    test_memory_integration()
```

---

## Reference Documentation

- **Full System Guide**: See `MEMORY_SYSTEM_USER_GUIDE.md` (2,268 lines, comprehensive)
- **Quick Reference**: See `ADAPTIVE_MEMORY_QUICK_REFERENCE.md` (agent-friendly)
- **API Endpoints**: See `API_REFERENCE.md` for REST API documentation
- **Neo4j Queries**: See `neo4j_query_examples.md` for graph database patterns
- **MCP Integration**: See `.claude/mcp.json` for Memory Keeper configuration

---

## Getting Help

- **Question**: How do I know if my command was saved?
  **Answer**: Call "show memory status" to see all saved memories

- **Question**: What if the memory backend is down?
  **Answer**: Implement fallback to local SQLite, then sync when backend returns

- **Question**: Can I customize the importance weighting?
  **Answer**: Yes, modify the calculate_importance() weights in your integration

- **Question**: How do I restore agent identity after restart?
  **Answer**: Call restore_identity() at agent startup, reads from Neo4j graph

- **Question**: What's the difference between batch and immediate vectorization?
  **Answer**: Immediate = searchable now, Batch = searchable after 50 items queued

---

## Next Steps

1. Choose integration pattern (MCP / API / Embedded)
2. Implement command detection with provided regex patterns
3. Add importance scoring and tier classification
4. Connect to backend storage (Memory Keeper / Neo4j / Milvus)
5. Implement response formatting for user feedback
6. Test all 11 commands with sample inputs
7. Deploy and monitor memory operations
8. Document your agent's memory capabilities

**Good luck with your integration!**
