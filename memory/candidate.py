# memory/candidate.py
from typing import List, Optional
from .models import ShortTermMemory, CandidateMemory
from .llm_client import LLMClient

class CandidateManager:
    """
    阶段 2：候选记忆管理器
    负责：判断短期记忆是否具有“长期复用价值”，并为其分配 AFS 抽屉。
    """
    
    def __init__(self):
        self.candidates: List[CandidateMemory] = []
        self.llm_client = LLMClient()
        
    def evaluate_stm(self, stm: ShortTermMemory) -> Optional[CandidateMemory]:
        """
        使用 LLM 评估短期记忆，决定是否生成候选记忆。
        这里利用大模型来判断记忆的“复用价值”和“AFS 抽屉归属”。
        """
        # 构建 Prompt，引导 LLM 进行记忆过滤与路由
        prompt = f"""
你是一个智能记忆过滤与路由专家。请阅读以下用户的短期对话摘要，判断其中是否包含值得长期记录的个人画像(profile)、偏好(preferences)或关键事件(events)。

【对话摘要内容】
话题: {stm.topic}
内容: {stm.summary}

【处理指令】
1. 如果没有任何长期复用价值（如：寒暄、无意义的闲聊、瞬时性且无后续参考价值的信息），请返回 JSON: {{"has_value": false}}。
2. 如果有价值，请提取核心事实（注意：要把“我”转换成“用户”），并分配给最合适的抽屉（可选：profile, preferences, entities, events），返回 JSON: 
{{
  "has_value": true, 
  "drawer": "preferences", 
  "extracted_content": "用户喜欢吃滨寿司，不再喜欢寿司朗", 
  "confidence": 0.9
}}。

请直接输出 JSON 结果。
"""
        
        # 调用 LLM 进行评估
        result = self.llm_client.call_llm_json(prompt)
        
        # 如果调用失败或判断无价值，返回 None
        if not result or not result.get("has_value"):
            return None

        # 提取 LLM 返回的结构化数据
        target_drawer = result.get("drawer", "entities") # 默认归入 entities
        extracted_content = result.get("extracted_content", stm.summary)
        confidence = result.get("confidence", 0.8)

        # 生成候选记忆
        candidate = CandidateMemory(
            content=extracted_content,
            target_drawer=target_drawer,
            confidence=confidence,
            source_stm=stm
        )
        self.candidates.append(candidate)
        return candidate