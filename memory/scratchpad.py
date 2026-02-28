# memory/scratchpad.py
from typing import List, Optional
from .models import Message, ShortTermMemory

class ScratchpadManager:
    """
    阶段 1：短期工作记忆管理器 (参考 LightMem 效率派思路)
    负责：入口过滤（扔掉废话）和 话题聚合（打包上下文）。
    """
    
    def __init__(self):
        # 存储原始对话流，用于溯源
        self.raw_history: List[Message] = []
        # 存储聚合后的短期记忆块
        self.short_term_memories: List[ShortTermMemory] = []
        # 记录已被聚合的消息 ID，避免重复处理
        self.aggregated_msg_ids: set = set()
        
    def add_message(self, message: Message) -> None:
        """
        接收新消息并进行轻量级过滤。
        入口过滤的作用是避免将无意义的“寒暄”或“语气词”存入聚合池，从而减少后续处理的噪音。
        """
        # 定义常见的无意义寒暄词和语气词
        meaningless_words = {
            "嗯", "好的", "没问题", "哦", "哈喽", "你好", "哈", "呵", 
            "嗯嗯", "好的呢", "收到", "OK", "ok", "了解", "知道了"
        }
        
        # 过滤规则：
        # 1. 清理空白符和常见的标点符号后再判断
        content_clean = message.content.strip().rstrip("!！?？.。~")
        
        # 2. 如果清理后的内容在无意义词库中，或者长度小于 2（排除掉单个汉字或符号）
        if content_clean in meaningless_words or len(content_clean) < 2:
            message.is_meaningful = False
            
        # 将消息存入原始历史记录
        self.raw_history.append(message)

    def trigger_aggregation(self) -> Optional[ShortTermMemory]:
        """
        将当前积累的有效消息聚合成一个短期记忆条目。
        话题聚合的作用是将零散的消息打包成有意义的上下文块，避免记忆库碎片化。
        """
        # 1. 提取所有有意义且尚未被聚合的消息
        valid_pending_messages = [
            m for m in self.raw_history 
            if m.is_meaningful and m.msg_id not in self.aggregated_msg_ids
        ]

        # 2. 触发规则：达到 3 条有效消息即进行聚合
        if len(valid_pending_messages) >= 3:
            # 选取本次待聚合的消息批次（前 3 条）
            batch = valid_pending_messages[:3]
            
            # 生成 ShortTermMemory 对象
            stm = ShortTermMemory(
                topic="提取的临时话题",  # 占位符：后续可接入 LLM 提取
                summary=" | ".join([m.content for m in batch]),  # 朴素拼接作为摘要
                source_msg_ids=[m.msg_id for m in batch]
            )
            
            # 记录聚合结果并标记消息已处理
            self.short_term_memories.append(stm)
            for m in batch:
                self.aggregated_msg_ids.add(m.msg_id)
                
            return stm
            
        # 不满足聚合阈值时返回 None
        return None