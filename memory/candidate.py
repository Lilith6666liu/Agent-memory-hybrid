# memory/candidate.py
from typing import List, Optional
from .models import ShortTermMemory, CandidateMemory

class CandidateManager:
    """
    阶段 2：候选记忆管理器
    负责：判断短期记忆是否具有“长期复用价值”，并为其分配 AFS 抽屉。
    """
    
    def __init__(self):
        self.candidates: List[CandidateMemory] = []
        
    def evaluate_stm(self, stm: ShortTermMemory) -> Optional[CandidateMemory]:
        """
        评估短期记忆，决定是否生成候选记忆。
        这里模拟了 LightMem 的 Candidate 提取（复用价值判断），以及 OpenViking 的 AFS 路由分配（抽屉归类）。
        """
        target_drawer = None
        text_to_check = f"{stm.topic} {stm.summary}"

        # 规则 A (Profile): 个人基本信息
        if any(keyword in text_to_check for keyword in ["我是", "我叫", "我的名字"]):
            target_drawer = "profile"
        
        # 规则 B (Preferences): 用户偏好
        elif any(keyword in text_to_check for keyword in ["喜欢", "爱吃", "偏好", "不喜欢"]):
            target_drawer = "preferences"
            
        # 规则 C (Events): 关键事件
        elif any(keyword in text_to_check for keyword in ["昨天", "发生", "会议"]):
            target_drawer = "events"

        # 如果匹配成功，生成候选记忆
        if target_drawer:
            candidate = CandidateMemory(
                content=stm.summary,      # 暂时直接使用摘要内容
                target_drawer=target_drawer,
                confidence=0.85,          # 模拟高置信度
                source_stm=stm
            )
            self.candidates.append(candidate)
            return candidate

        # 不具备长期价值，忽略
        return None