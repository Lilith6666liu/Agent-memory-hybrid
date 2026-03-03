# 🧠 Agent Memory Hybrid

[![CI](https://github.com/Lilith6666liu/Agent-memory-hybrid/actions/workflows/ci.yml/badge.svg)](https://github.com/Lilith6666liu/Agent-memory-hybrid/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **A production-ready semantic memory system for AI agents.**

Combines the best ideas from [OpenViking](https://github.com/OpenViking/OpenViking) (AFS drawer structure) and [LightMem](https://github.com/HKU-Smart-Lab/LightMem) (async sleep updates), with modern **embedding-based semantic conflict detection**.

[中文介绍](#中文介绍)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🗂️ **AFS Drawer System** | Organized memory storage (profile, preferences, entities, events, etc.) |
| ⚡ **Async Processing** | Non-blocking daytime operation + batch nighttime updates |
| 🔍 **Semantic Conflict Detection** | Embedding-based similarity matching, not hardcoded keywords |
| 🔄 **Version Evolution** | Non-destructive updates with `active` → `deprecated` tracking |
| 🔎 **Semantic Search** | Retrieve memories by meaning, not just keywords |
| 📦 **Production Ready** | pip installable, fully tested, type-annotated |

---

## 🚀 Quick Start

### Installation

```bash
pip install agent-memory-hybrid
```

### Configuration

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.siliconflow.cn/v1  # or your provider
LLM_MODEL=Qwen/Qwen2.5-7B-Instruct
EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5
```

### Basic Usage

```python
from memory import ScratchpadManager, CandidateManager, MemoryManager, Message

# Initialize
scratchpad = ScratchpadManager(aggregation_threshold=3)
candidate_mgr = CandidateManager()
memory_mgr = MemoryManager(db_path="agent_memory.db")

# Add messages
messages = [
    Message(role="user", content="I love sushi", msg_id="1"),
    Message(role="user", content="It's my favorite food", msg_id="2"),
    Message(role="user", content="I go every weekend", msg_id="3"),
]

for msg in messages:
    scratchpad.add_message(msg)

# Aggregate into short-term memory
stm = scratchpad.trigger_aggregation()

# Evaluate and extract candidate
if stm:
    candidate = candidate_mgr.evaluate_stm(stm)
    if candidate:
        memory_mgr.enqueue_candidate(candidate)

# Batch process (sleep update)
stats = memory_mgr.run_sleep_update()
print(f"Inserted: {stats['inserted']}, Deprecated: {stats['deprecated']}")

# Query memories
memories = memory_mgr.get_active_memories(drawer="preferences")
memory_mgr.print_active_memories()
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  History Layer                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Raw messages (user/assistant)                        │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │ Entry filtering                      │
│                       ▼                                      │
│  Scratchpad Layer (LightMem)                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Short-term memory (aggregated context blocks)        │   │
│  │ • Topic extraction via LLM                           │   │
│  │ • Filler word filtering                              │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │ LLM evaluation                       │
│                       ▼                                      │
│  Candidate Layer                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Candidate memories (value-assessed, with embeddings) │   │
│  │ • Drawer assignment                                  │   │
│  │ • Embedding generation                               │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │ Async queue                          │
│                       ▼                                      │
│  Memory Layer (OpenViking AFS)                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Long-term storage (SQLite + embeddings)              │   │
│  │ • Semantic conflict detection                        │   │
│  │ • Version evolution (active/deprecated)              │   │
│  │ • Semantic search                                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Semantic Conflict Detection

Unlike keyword-based systems, we use **embedding similarity** to detect conflicts:

```python
# Old memory: "user likes sushi"
# New memory: "user prefers ramen instead"

# These are detected as conflicts because their embeddings
# are semantically similar (both about food preferences)
# even though they don't share keywords!

stats = memory_mgr.run_sleep_update()
# stats: {"inserted": 1, "deprecated": 1}
# Old sushi memory is deprecated, new ramen memory is active
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=memory --cov-report=html

# Specific test file
pytest tests/test_embedding_utils.py -v
```

---

## 📚 API Reference

### ScratchpadManager

```python
from memory import ScratchpadManager

manager = ScratchpadManager(aggregation_threshold=3)
manager.add_message(message: Message) -> None
stm = manager.trigger_aggregation() -> Optional[ShortTermMemory]
```

### CandidateManager

```python
from memory import CandidateManager

manager = CandidateManager()
candidate = manager.evaluate_stm(stm: ShortTermMemory) -> Optional[CandidateMemory]
```

### MemoryManager

```python
from memory import MemoryManager

manager = MemoryManager(
    db_path="agent_memory.db",
    conflict_threshold=0.75  # cosine similarity threshold
)

manager.enqueue_candidate(candidate: CandidateMemory) -> None
stats = manager.run_sleep_update() -> Dict[str, int]
memories = manager.get_active_memories(drawer: Optional[str]) -> List[Dict]
results = manager.search_similar(query_embedding: List[float], top_k=5) -> List[Dict]
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- [OpenViking](https://github.com/OpenViking/OpenViking) - AFS drawer structure inspiration
- [LightMem](https://github.com/HKU-Smart-Lab/LightMem) - Async processing inspiration

---

# 中文介绍

## 🧠 Agent Memory Hybrid

> **面向 AI Agent 的生产级语义记忆系统**

融合 [OpenViking](https://github.com/OpenViking/OpenViking) 的 AFS 抽屉式结构和 [LightMem](https://github.com/HKU-Smart-Lab/LightMem) 的异步睡眠更新机制，并加入现代的 **基于 Embedding 的语义冲突检测**。

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🗂️ **AFS 抽屉系统** | 有序的记忆存储（画像、偏好、实体、事件等） |
| ⚡ **异步处理** | 白天非阻塞实时处理 + 夜间批量更新 |
| 🔍 **语义冲突检测** | 基于 Embedding 相似度匹配，非硬编码关键词 |
| 🔄 **版本演化** | 非破坏性更新，`active` → `deprecated` 状态追踪 |
| 🔎 **语义搜索** | 按含义检索记忆，非仅关键词匹配 |
| 📦 **生产就绪** | 支持 pip 安装、完整测试、类型注解 |

## 🚀 快速开始

```bash
pip install agent-memory-hybrid
```

```python
from memory import ScratchpadManager, CandidateManager, MemoryManager, Message

# 初始化
scratchpad = ScratchpadManager(aggregation_threshold=3)
candidate_mgr = CandidateManager()
memory_mgr = MemoryManager(db_path="agent_memory.db")

# 添加消息并处理
for msg in messages:
    scratchpad.add_message(msg)

stm = scratchpad.trigger_aggregation()
if stm:
    candidate = candidate_mgr.evaluate_stm(stm)
    if candidate:
        memory_mgr.enqueue_candidate(candidate)

# 批量处理
stats = memory_mgr.run_sleep_update()
```

## 🔍 语义冲突检测示例

```python
# 旧记忆："用户喜欢寿司"
# 新记忆："用户更喜欢拉面了"

# 系统通过 Embedding 相似度检测到这是同一类偏好（食物偏好）的更新
# 自动将旧记忆标记为 deprecated，新记忆标记为 active

stats = memory_mgr.run_sleep_update()
# 结果：{"inserted": 1, "deprecated": 1}
```

## 🏗️ 架构设计

四层记忆流转架构：
1. **History** - 原始对话消息
2. **Scratchpad** - 短期工作记忆（聚合、过滤）
3. **Candidate** - 候选记忆（LLM 评估、Embedding 生成）
4. **Memory** - 长期记忆（AFS 存储、语义冲突检测）
