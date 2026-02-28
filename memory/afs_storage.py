# memory/afs_storage.py
import uuid
from datetime import datetime
from typing import List
from .models import AgenticFileSystem, CandidateMemory, MemoryItem

class MemoryManager:
    """
    阶段 3：长期记忆与睡眠后台管理器 (融合 OpenViking 与 LightMem)
    负责：将 Candidate 落盘到 AFS，处理冲突，管理版本演化。
    """
    
    def __init__(self):
        self.afs = AgenticFileSystem()
        self.candidate_queue: List[CandidateMemory] = [] # 模拟后台队列
        
    def enqueue_candidate(self, candidate: CandidateMemory) -> None:
        """
        白天（实时对话中）：仅做轻量级入队，不阻塞主流程。
        这里体现了 LightMem 的异步处理思想，确保用户感知的响应速度。
        """
        self.candidate_queue.append(candidate)
        
    def run_sleep_update(self) -> None:
        """
        夜间/空闲时：触发睡眠任务，批量处理候选队列。
        这里模拟了知识图谱/大模型在后台进行实体对齐和冲突消解的过程（OpenViking 的版本演化思想）。
        """
        now = datetime.now()
        
        for candidate in self.candidate_queue:
            # 1. 映射抽屉：根据 target_drawer 找到 AFS 中对应的列表
            # 使用 getattr 动态获取属性（如 'preferences' -> self.afs.preferences）
            drawer_name = candidate.target_drawer
            if not hasattr(self.afs, drawer_name):
                continue
            
            drawer_list: List[MemoryItem] = getattr(self.afs, drawer_name)
            
            # 2. 模拟冲突检测 (以 '寿司' 为例进行实体对齐)
            # 这里模拟了后台扫描现有记忆，判断新旧知识是否冲突
            for item in drawer_list:
                if item.status == 'active':
                    # 教学演示：如果新旧内容都包含 "寿司"，则判定为偏好更新（发生冲突）
                    if "寿司" in candidate.content and "寿司" in item.content:
                        # 3. 版本演化处理：一旦发现冲突，标记旧记录为 deprecated
                        # 体现了 Append-only 的数据审计思想，不直接删除旧数据
                        item.status = 'deprecated'
                        item.updated_at = now
            
            # 4. 创建并插入新记忆
            new_item = MemoryItem(
                item_id=str(uuid.uuid4()),
                content=candidate.content,
                status='active',
                created_at=now,
                updated_at=now
            )
            drawer_list.append(new_item)
            
        # 5. 处理完队列后清空
        self.candidate_queue.clear()