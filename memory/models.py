# memory/models.py
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

# ==========================================
# 基础消息层 (History)
# ==========================================
@dataclass
class Message:
    """原始对话消息 (History)"""
    role: str          # 'user' 或 'assistant'
    content: str       # 消息文本
    msg_id: str        # 唯一消息ID
    timestamp: datetime = field(default_factory=datetime.now) # 发生时间
    is_meaningful: bool = True # 是否有意义（用于入口过滤标记）

# ==========================================
# 状态机中间层 (Scratchpad & Candidate)
# ==========================================
@dataclass
class ShortTermMemory:
    """短期工作记忆条目 (Scratchpad)
    将多轮相关的对话聚合成一个上下文块，避免碎片化。
    参考: LightMem 的 Working Memory 概念
    """
    topic: str              # 聚合的话题，例如 "餐厅偏好"
    summary: str            # 对话摘要
    source_msg_ids: List[str] # 来源消息ID列表，方便追溯
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class CandidateMemory:
    """候选记忆条目 (Candidate)
    经过评估，认为“有长期复用价值”的信息，等待进入 AFS。
    """
    content: str            # 提取出的核心知识，如 "用户喜欢吃滨寿司"
    target_drawer: str      # 拟归属的 AFS 抽屉，如 "Preferences"
    confidence: float       # 置信度 (0-1)，用于后续决策
    source_stm: ShortTermMemory # 关联的短期记忆来源

# ==========================================
# 长期记忆层 (OpenViking AFS Drawers)
# ==========================================
@dataclass
class MemoryItem:
    """长期记忆的基础单元，支持版本演化"""
    item_id: str
    content: str            # 记忆内容
    status: str             # 'active' (当前有效), 'deprecated' (已过期/被覆盖)
    created_at: datetime
    updated_at: datetime

@dataclass
class AgenticFileSystem:
    """AFS 虚拟文件系统 (参考 OpenViking)
    把记忆分门别类，避免变成电子垃圾场。
    """
    # 用户侧
    profile: List[MemoryItem] = field(default_factory=list)      # 我是谁
    preferences: List[MemoryItem] = field(default_factory=list)  # 我偏好什么
    entities: List[MemoryItem] = field(default_factory=list)     # 我常提到的人/物
    events: List[MemoryItem] = field(default_factory=list)       # 关键事件

    # Agent侧
    cases: List[MemoryItem] = field(default_factory=list)        # 典型案例
    patterns: List[MemoryItem] = field(default_factory=list)     # 可复用的模式规则
