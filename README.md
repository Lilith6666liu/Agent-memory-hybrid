# Agent Memory Hybrid PoC

这是一个结合了 **OpenViking** (AFS 抽屉式结构) 和 **LightMem** (睡眠更新机制) 思想的 Agent 记忆状态机原型系统 (Proof of Concept)。

## 🚀 项目简介

在构建复杂的企业级数字员工（Digital Employees）时，Agent 如何处理长短期记忆的演化是一个巨大挑战。本项目旨在演示一种平衡“实时对话响应速度”与“长期记忆一致性”的混合架构：
- **白天模式 (实时)**：采用 LightMem 的无阻塞思想，快速过滤噪音，将有效上下文打包暂存。
- **夜间模式 (后台)**：采用 OpenViking 的 AFS (Agentic File System) 版本演化思想，进行实体对齐、冲突消解与长期存储。

## 🏗️ 核心架构 (v0.3 更新)

记忆在系统中的流转过程如下：

1.  **History (原始消息)**: 接收用户或助手的原始对话流。
2.  **Scratchpad (短期工作记忆)**: 
    - **入口过滤**: 剔除无意义的寒暄。
    - **话题聚合**: 将散碎的消息打包成有意义的上下文块 (STM)。
3.  **Candidate (候选记忆)**: 
    - **LLM 评估 (v0.3)**: 真正接入大模型（如 Qwen2.5-7B），自动判断复用价值并分配抽屉。
    - **AFS 路由**: 根据 LLM 意图分配存储抽屉。
4.  **Memory (长期记忆/AFS)**: 
    - **SQLite 持久化 (v0.3)**: 记忆不再随程序关闭而丢失，全量落盘至 `agent_memory.db`。
    - **版本演化**: 在 SQL 层通过 `active` -> `deprecated` 状态切换实现非破坏性更新。

## 🛠️ 快速开始

### 运行环境
- Python 3.8+
- 依赖：`pip install openai python-dotenv requests`

### 配置 (v0.3)
在项目根目录创建 `.env` 文件并填入：
```env
OPENAI_API_KEY=你的API_KEY
OPENAI_BASE_URL=https://api.siliconflow.cn/v1
LLM_MODEL=Qwen/Qwen2.5-7B-Instruct
```

### 运行 Demo
```bash
python3 examples/run_demo.py
```
或运行专门的持久化验证脚本：
```bash
python3 verify_sqlite_memory.py
```

### 预期输出
你将看到控制台详细展示了以下流程：
- 过滤掉无意义对话。
- 提取出用户偏好（例如：喜欢寿司朗）。
- **模拟偏好变更**: 当用户第二天说“更喜欢滨寿司”时，后台如何自动将旧偏好标记为 `deprecated` 并建立新偏好。

## 🙏 致谢

本项目的设计灵感深受以下开源项目的启发：
- [OpenViking](https://github.com/OpenViking/OpenViking): 提供了 AFS 虚拟文件系统与记忆抽屉的结构化思路。
- [LightMem](https://github.com/HKU-Smart-Lab/LightMem): 提供了 Working Memory 与后台异步睡眠更新的效率优化思路。

---
*本项目仅供教学与 PoC 演示使用。*
