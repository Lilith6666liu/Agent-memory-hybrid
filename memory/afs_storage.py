# memory/afs_storage.py
import uuid
import sqlite3
from datetime import datetime
from typing import List, Dict
from .models import CandidateMemory

class MemoryManager:
    """
    阶段 3：长期记忆与 SQLite 持久化存储 (融合 OpenViking 与 LightMem)
    负责：将 Candidate 落盘到 SQLite 数据库，处理冲突，管理版本演化。
    """
    
    def __init__(self, db_path: str = "agent_memory.db"):
        # 连接本地数据库：这相当于 OpenViking 架构中的落盘操作准备
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()
        self.candidate_queue: List[CandidateMemory] = [] # 依然保留作为白天的内存暂存队列
        
    def _create_table(self):
        """编写 SQL 创建名为 afs_memory 的表（如果不存在）"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS afs_memory (
                id TEXT PRIMARY KEY,
                drawer TEXT,
                content TEXT,
                status TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        self.conn.commit()

    def enqueue_candidate(self, candidate: CandidateMemory) -> None:
        """
        白天（实时对话中）：仅做轻量级入队，不阻塞主流程。
        这里体现了 LightMem 的异步处理思想，确保用户感知的响应速度。
        """
        self.candidate_queue.append(candidate)
        
    def run_sleep_update(self) -> None:
        """
        夜间/空闲时：触发睡眠任务，批量处理候选队列。
        这里模拟了在后台进行实体对齐和冲突消解的过程（OpenViking 的版本演化思想）。
        """
        now = datetime.now().isoformat()
        cursor = self.conn.cursor()
        
        for candidate in self.candidate_queue:
            drawer_name = candidate.target_drawer
            
            # 1. 模拟冲突检测 (SQL 版)：根据 candidate 的 target_drawer，在数据库中 SELECT 出该抽屉下所有 status='active' 的记录
            cursor.execute(
                "SELECT id, content FROM afs_memory WHERE drawer = ? AND status = 'active'", 
                (drawer_name,)
            )
            active_items = cursor.fetchall()
            
            # 2. 判定冲突（教学演示逻辑：如果旧内容包含 "寿司"，则判定为偏好更新）
            for item_id, item_content in active_items:
                if "寿司" in candidate.content and "寿司" in item_content:
                    # 3. 版本演化（SQL 版）：执行 UPDATE 语句，将旧记录标记为 deprecated
                    # 这体现了 Append-only 的数据审计思想，记录版本演化轨迹
                    cursor.execute(
                        "UPDATE afs_memory SET status = 'deprecated', updated_at = ? WHERE id = ?",
                        (now, item_id)
                    )
            
            # 4. 写入新记忆：执行 INSERT 语句，将当前 candidate 生成的新记录写入库中
            new_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO afs_memory (id, drawer, content, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (new_id, drawer_name, candidate.content, 'active', now, now)
            )
            
        # 5. 遍历完成后，执行 commit，并清空队列
        self.conn.commit()
        self.candidate_queue.clear()

    def print_active_memories(self) -> None:
        """
        执行 SELECT 查询，查出所有 status='active' 的记忆，并按 drawer 分类打印
        方便观察 SQLite 落盘效果。
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT drawer, content, created_at FROM afs_memory WHERE status = 'active' ORDER BY drawer")
        results = cursor.fetchall()

        if not results:
            print("\n[AFS SQLite] 目前没有活跃的长期记忆。")
            return

        print(f"\n{'='*20} AFS 活跃记忆 (SQLite 持久化) {'='*20}")
        current_drawer = None
        for drawer, content, created_at in results:
            if drawer != current_drawer:
                print(f"\n📂 Drawer: [{drawer}]")
                current_drawer = drawer
            print(f"  - {content} (记录于: {created_at})")
        print(f"\n{'='*60}")