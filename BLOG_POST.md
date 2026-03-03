# 从 0 Star 到可用：我是如何重构一个 Agent 记忆系统的

> 原标题：Building a Production-Ready Agent Memory System: From Toy Code to Real Architecture

## 引言

两个月前，我在 GitHub 上放了一个 Agent 记忆系统的原型项目。想法很好——结合 OpenViking 的 AFS 抽屉结构和 LightMem 的异步更新机制——但代码质量嘛...怎么说呢，用 "寿司" 字符串匹配来检测记忆冲突，这能叫生产代码吗？

结果可想而知：**0 star，0 fork，0 issue**。无人问津。

这篇文章记录了我如何把它从"教学演示"改造成"可用开源项目"的全过程。如果你也在做类似的事情，希望这些经验能帮到你。

---

## 问题诊断：为什么没人看？

### 1. 硬编码的玩具逻辑

原代码里的冲突检测是这样的：

```python
# 原代码 -  literally 硬编码
if "寿司" in candidate.content and "寿司" in item_content:
    # 判定为冲突...
```

这意味着什么？用户如果说"我喜欢披萨"，系统完全无法处理偏好变更。整个冲突检测系统只对"寿司"有效。

### 2. 没有 embedding，没有语义理解

现代 RAG 系统的核心是什么？是向量检索、语义相似度。原项目完全没有这些，只有朴素的字符串匹配。

### 3. 工程化程度为零

- 没有 `setup.py`，别人没法 `pip install`
- 没有单元测试
- 没有 CI/CD
- README 只有中文，没有英文

### 4. 没有差异化价值

市面上已经有 Mem0、MemGPT、Zep 等成熟方案。如果新项目没有独特优势，为什么要用它？

---

## 重构策略

我给自己定了四个目标：

1. **核心能力升级**：用 embedding + 余弦相似度替换硬编码
2. **工程化改造**：加上 pip 包结构、单元测试、CI/CD
3. **国际化**：重写双语 README
4. **内容营销**：写一篇技术博客（就是你现在看的这篇）

---

## 核心改造：语义冲突检测

### 新架构设计

```
History → Scratchpad (STM) → Candidate → Memory (LTM/AFS)
   ↓           ↓                ↓            ↓
原始消息    话题聚合         LLM评估      Embedding存储
          LLM提取主题      Embedding    语义冲突检测
```

### 关键改动 1：Embedding 生成

```python
# memory/llm_client.py
class LLMClient:
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for semantic comparison."""
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding
```

### 关键改动 2：余弦相似度冲突检测

```python
# memory/embedding_utils.py
import math
from typing import List

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0
```

### 关键改动 3：语义冲突检测实战

```python
# memory/afs_storage.py
def run_sleep_update(self) -> Dict[str, int]:
    for candidate in self.candidate_queue:
        # 1. 获取同抽屉的所有 active 记忆
        active_items = self._get_active_with_embeddings(candidate.target_drawer)

        # 2. 语义冲突检测
        conflict_id, score = find_most_similar(
            candidate.embedding,
            [(item.id, item.embedding) for item in active_items],
            threshold=self.conflict_threshold  # 默认 0.75
        )

        # 3. 如果相似度超过阈值，标记旧记忆为 deprecated
        if conflict_id:
            self._deprecate_memory(conflict_id)

        # 4. 插入新记忆
        self._insert_memory(candidate)
```

### 效果对比

| 场景 | 原系统 | 新系统 |
|------|--------|--------|
| "我喜欢寿司" → "我喜欢拉面" | ❌ 无法检测（关键词不同） | ✅ 语义相似，触发冲突 |
| "我喜欢寿司朗" → "我讨厌寿司朗" | ✅ 能检测（都含"寿司"） | ✅ 语义相似，触发冲突 |
| "我喜欢寿司" → "今天天气不错" | ✅ 不冲突 | ✅ 语义不相似，不冲突 |

---

## 工程化改造

### 1. 包结构改造

原项目结构：
```
Agent-memory-hybrid/
  memory/
    *.py
  examples/
    run_demo.py
  README.md
```

新结构：
```
Agent-memory-hybrid/
  memory/                 # 核心包
    __init__.py          # 统一导出
    models.py            # 数据模型
    scratchpad.py        # 短期记忆
    candidate.py         # 候选评估
    afs_storage.py       # 长期存储
    llm_client.py        # LLM 客户端
    embedding_utils.py   # 向量工具
  tests/                 # 单元测试
    test_*.py
  examples/              # 示例代码
  .github/workflows/     # CI/CD
    ci.yml
  pyproject.toml         # 现代 Python 包配置
  README.md              # 双语文档
```

### 2. pyproject.toml 配置

```toml
[project]
name = "agent-memory-hybrid"
version = "0.4.0"
description = "A semantic memory system for AI agents"
readme = "README.md"
requires-python = ">=3.9"

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]
```

### 3. 单元测试覆盖

```python
# tests/test_afs_storage.py
def test_semantic_conflict_detection(self, manager):
    """Should detect conflicts via embedding similarity."""
    stm = ShortTermMemory(topic="food", summary="test", source_msg_ids=["1"])

    # First memory
    c1 = CandidateMemory("user likes pizza", "preferences", 0.9, stm, [1.0, 0.0, 0.0])
    manager.enqueue_candidate(c1)
    manager.run_sleep_update()

    # Similar memory (should conflict)
    c2 = CandidateMemory("user prefers pasta", "preferences", 0.9, stm, [0.95, 0.1, 0.0])
    manager.enqueue_candidate(c2)
    stats = manager.run_sleep_update()

    assert stats["deprecated"] == 1
    assert stats["inserted"] == 1
```

### 4. GitHub Actions CI

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - run: ruff check memory tests
      - run: black --check memory tests
      - run: mypy memory
      - run: pytest --cov=memory
```

---

## README 重写策略

### 原 README 的问题

- 只有中文，国际化受众为零
- 没有 badges（CI status、Python version、License）
- 没有快速开始代码示例
- 没有架构图
- 没有 API 文档

### 新 README 结构

```markdown
# Agent Memory Hybrid

[Badges: CI, Python version, License]

> One-line description

## Features (表格展示)

## Quick Start (pip install + 代码示例)

## Architecture (ASCII 架构图)

## Semantic Conflict Detection (核心卖点详细解释)

## Testing

## API Reference

## 中文介绍 (保留中文受众)
```

---

## 营销与推广

技术再好，没人知道等于零。我的推广策略：

### 1. 内容营销

- **技术博客**（本文）：发布到知乎、掘金、CSDN
- **Twitter/X 线程**：拆解核心设计决策
- **Reddit**：r/LocalLLaMA, r/MachineLearning

### 2. 社区参与

- 在相关项目的 issue/PR 中提及（如果合适）
- 回答 Stack Overflow 上关于 Agent memory 的问题
- 参与 Discord/Slack 社区的讨论

### 3. 持续迭代

- 根据反馈快速迭代
- 保持 commit 活跃
- 及时回复 issue

---

## 总结：从 0 Star 学到了什么

### 1. 代码质量是底线

"寿司硬编码"这种代码，自己写着玩可以，放出来就是浪费时间。要么不做，要做就做到 pip install 能用的程度。

### 2. 差异化很重要

市面上不缺记忆系统。你的项目解决了什么别人没解决的问题？我们的答案是：**开箱即用的语义冲突检测**。

### 3. 文档即产品

README 是门面。没有好的文档，再好的代码也无人问津。

### 4. 推广是必要工作

"酒香不怕巷子深"在技术圈不适用。好的项目需要主动推广。

---

## 项目链接

- **GitHub**: https://github.com/Lilith6666liu/Agent-memory-hybrid
- **文档**: README.md（双语）
- **安装**: `pip install agent-memory-hybrid`

如果你对这个项目感兴趣，欢迎 star、fork、提 issue。也欢迎贡献代码！

---

*本文同时发布于 [GitHub](https://github.com/Lilith6666liu/Agent-memory-hybrid) 和 [知乎/掘金]*
