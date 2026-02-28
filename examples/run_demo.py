# examples/run_demo.py
import sys
import os
from datetime import datetime

# 把父目录加入系统路径，确保能引入 memory 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.models import Message
from memory.scratchpad import ScratchpadManager
from memory.candidate import CandidateManager
from memory.afs_storage import MemoryManager

def print_divider(title):
    print(f"\n{'='*20} {title} {'='*20}")

def print_afs_status(memory_mgr):
    print("\n--- [AFS 长期记忆库当前状态] ---")
    print(f"Preferences (偏好抽屉):")
    for item in memory_mgr.afs.preferences:
        print(f"  - ID: {item.item_id[:8]}... | Status: [{item.status}] | Content: {item.content[:50]}...")

def main():
    print("=== 初始化 Agent Memory 混合架构 PoC (偏好演化演示) ===\n")
    
    # 实例化三个状态机管家
    scratchpad_mgr = ScratchpadManager()
    candidate_mgr = CandidateManager()
    memory_mgr = MemoryManager()

    # =========================================================
    # 第一天：建立初始偏好 (喜欢寿司朗)
    # =========================================================
    print_divider("第一天：建立初始偏好")
    
    day1_history = [
        Message(role="user", content="你好啊", msg_id="d1_m1"), # 无意义，应被过滤
        Message(role="user", content="我最近真是太喜欢吃寿司朗了，每周都要去", msg_id="d1_m2"),
        Message(role="user", content="寿司朗的三文鱼真的很绝", msg_id="d1_m3"),
        Message(role="assistant", content="确实，我也听很多用户提过寿司朗。", msg_id="d1_m4") # 凑够3条有效信息触发聚合
    ]

    print("--- [白天实时对话] ---")
    for msg in day1_history:
        print(f"收到消息: [{msg.role}] {msg.content}")
        scratchpad_mgr.add_message(msg)
    
    # 触发聚合 (Scratchpad -> STM)
    stm1 = scratchpad_mgr.trigger_aggregation()
    if stm1:
        print(f"\n【阶段1】生成的短期记忆 (STM):\n  Topic: {stm1.topic}\n  Summary: {stm1.summary}")
        
        # 提取候选 (STM -> Candidate)
        candidate1 = candidate_mgr.evaluate_stm(stm1)
        if candidate1:
            print(f"\n【阶段2】提取的候选记忆 (Candidate):\n  Target Drawer: {candidate1.target_drawer}\n  Confidence: {candidate1.confidence}")
            
            # 模拟白天实时对话：仅暂存队列，不阻塞
            memory_mgr.enqueue_candidate(candidate1)
            print("\n【阶段3-白天】模拟 LightMem 异步处理：候选记忆已入队，实时对话保持轻量。")

    print("\n--- [夜晚后台处理] ---")
    # 模拟夜晚睡眠更新 (Candidate -> AFS)
    print("模拟后台 AFS 版本演化中...")
    memory_mgr.run_sleep_update()
    print_afs_status(memory_mgr)


    # =========================================================
    # 第二天：偏好冲突与演化 (移情滨寿司)
    # =========================================================
    print_divider("第二天：偏好冲突与演化")
    
    day2_history = [
        Message(role="user", content="昨天去吃了滨寿司", msg_id="d2_m1"),
        Message(role="user", content="发现滨寿司比寿司朗好吃多了，我以后更喜欢吃滨寿司了", msg_id="d2_m2"),
        Message(role="user", content="决定了，以后日料首选滨寿司", msg_id="d2_m3")
    ]

    print("--- [白天实时对话] ---")
    for msg in day2_history:
        print(f"收到消息: [{msg.role}] {msg.content}")
        scratchpad_mgr.add_message(msg)
    
    # 重复流程
    stm2 = scratchpad_mgr.trigger_aggregation()
    if stm2:
        print(f"\n【阶段1】生成的短期记忆 (STM):\n  Summary: {stm2.summary}")
        
        candidate2 = candidate_mgr.evaluate_stm(stm2)
        if candidate2:
            print(f"\n【阶段2】提取的候选记忆 (Candidate):\n  Target Drawer: {candidate2.target_drawer}")
            memory_mgr.enqueue_candidate(candidate2)
            
            print("\n【阶段3-白天】AFS 尚未更新，旧记忆依然是 active 状态。")
            print_afs_status(memory_mgr)

    print("\n--- [夜晚后台处理] ---")
    print("触发睡眠更新：后台正在进行实体对齐 (寿司) 与冲突消解...")
    memory_mgr.run_sleep_update()
    
    print_divider("全流程演示结束")
    print_afs_status(memory_mgr)
    print("\n[看点说明]：")
    print("1. 旧的 '寿司朗' 记忆现在已变为 [deprecated]，因为它被更有时效性的新偏好覆盖了。")
    print("2. 新的 '滨寿司' 记忆现在是 [active]，这体现了 OpenViking 的 AFS 版本演化思想。")

if __name__ == "__main__":
    main()
