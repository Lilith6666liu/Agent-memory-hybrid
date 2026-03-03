
from memory.afs_storage import MemoryManager
from memory.models import CandidateMemory, ShortTermMemory
import os

def test_sqlite_persistence():
    db_name = "test_agent_memory.db"
    if os.path.exists(db_name):
        os.remove(db_name)
    
    manager = MemoryManager(db_path=db_name)
    
    # 1. 模拟第一条记忆
    stm1 = ShortTermMemory(topic="饮食习惯", summary="用户喜欢滨寿司", source_msg_ids=["msg1"])
    candidate1 = CandidateMemory(
        content="用户喜欢吃滨寿司", 
        target_drawer="preferences", 
        confidence=0.9, 
        source_stm=stm1
    )
    
    print("--- 第一次入队 ---")
    manager.enqueue_candidate(candidate1)
    manager.run_sleep_update()
    manager.print_active_memories()
    
    # 2. 模拟冲突（包含“寿司”）
    stm2 = ShortTermMemory(topic="饮食更新", summary="用户现在更喜欢藏寿司", source_msg_ids=["msg2"])
    candidate2 = CandidateMemory(
        content="用户更喜欢吃藏寿司了", 
        target_drawer="preferences", 
        confidence=0.95, 
        source_stm=stm2
    )
    
    print("\n--- 第二次入队 (发生冲突) ---")
    manager.enqueue_candidate(candidate2)
    manager.run_sleep_update()
    manager.print_active_memories()

    # 3. 模拟不冲突的记忆
    stm3 = ShortTermMemory(topic="个人信息", summary="用户是一名程序员", source_msg_ids=["msg3"])
    candidate3 = CandidateMemory(
        content="用户是一名资深程序员", 
        target_drawer="profile", 
        confidence=1.0, 
        source_stm=stm3
    )
    
    print("\n--- 第三次入队 (不同 Drawer) ---")
    manager.enqueue_candidate(candidate3)
    manager.run_sleep_update()
    manager.print_active_memories()

    # 验证数据库中是否存在 deprecated 记录
    cursor = manager.conn.cursor()
    cursor.execute("SELECT content, status FROM afs_memory WHERE status = 'deprecated'")
    deprecated = cursor.fetchall()
    print(f"\n[验证] 已过期的记忆数量: {len(deprecated)}")
    for content, status in deprecated:
        print(f"  - {content} (状态: {status})")

    manager.conn.close()
    if os.path.exists(db_name):
        os.remove(db_name)

if __name__ == "__main__":
    test_sqlite_persistence()
