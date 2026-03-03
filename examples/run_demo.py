#!/usr/bin/env python3
"""
Demo script showing the full Agent Memory Hybrid pipeline.

This demonstrates:
  1. Day 1: Initial preference formation (user likes "Sushi Lang")
  2. Day 2: Preference evolution (user switches to "Bin Sushi")
  3. Semantic conflict detection via embeddings
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory import (
    ScratchpadManager,
    CandidateManager,
    MemoryManager,
    Message,
)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*20} {title} {'='*20}")


def main():
    print("🧠 Agent Memory Hybrid Demo")
    print("=" * 60)
    print("\nThis demo shows how the system handles preference evolution")
    print("using semantic conflict detection (not hardcoded keywords!).")

    # Initialize components
    scratchpad = ScratchpadManager(aggregation_threshold=3)
    candidate_mgr = CandidateManager()
    memory_mgr = MemoryManager(db_path="demo_memory.db", conflict_threshold=0.75)

    # =========================================================
    # Day 1: Establish initial preference
    # =========================================================
    print_section("Day 1: User discovers Sushi Lang")

    day1_messages = [
        Message(role="user", content="Hey there", msg_id="d1_1"),  # filtered
        Message(role="user", content="I tried Sushi Lang yesterday", msg_id="d1_2"),
        Message(role="user", content="The salmon was incredible!", msg_id="d1_3"),
        Message(role="assistant", content="Glad you enjoyed it!", msg_id="d1_4"),
    ]

    print("\n📥 Processing messages...")
    for msg in day1_messages:
        print(f"  [{msg.role}] {msg.content}")
        scratchpad.add_message(msg)

    # Aggregate and process
    stm1 = scratchpad.trigger_aggregation()
    if stm1:
        print(f"\n📦 STM created: {stm1.topic}")
        candidate1 = candidate_mgr.evaluate_stm(stm1)
        if candidate1:
            print(f"✨ Candidate: {candidate1.content[:50]}...")
            memory_mgr.enqueue_candidate(candidate1)

    print("\n🌙 Running sleep update...")
    stats1 = memory_mgr.run_sleep_update()
    print(f"   Inserted: {stats1['inserted']}, Deprecated: {stats1['deprecated']}")
    memory_mgr.print_active_memories()

    # =========================================================
    # Day 2: Preference change (semantic conflict!)
    # =========================================================
    print_section("Day 2: User switches to Bin Sushi")

    day2_messages = [
        Message(role="user", content="Went to Bin Sushi today", msg_id="d2_1"),
        Message(role="user", content="Way better than Sushi Lang!", msg_id="d2_2"),
        Message(role="user", content="I'm switching my go-to spot", msg_id="d2_3"),
    ]

    print("\n📥 Processing messages...")
    for msg in day2_messages:
        print(f"  [{msg.role}] {msg.content}")
        scratchpad.add_message(msg)

    stm2 = scratchpad.trigger_aggregation()
    if stm2:
        print(f"\n📦 STM created: {stm2.topic}")
        candidate2 = candidate_mgr.evaluate_stm(stm2)
        if candidate2:
            print(f"✨ Candidate: {candidate2.content[:50]}...")
            print(f"   Embedding generated for semantic comparison")
            memory_mgr.enqueue_candidate(candidate2)

    print("\n🌙 Running sleep update with conflict detection...")
    print("   (Comparing embeddings to detect semantic similarity)")
    stats2 = memory_mgr.run_sleep_update()
    print(f"   Inserted: {stats2['inserted']}, Deprecated: {stats2['deprecated']}")
    print("   → Old preference deprecated, new preference activated!")

    memory_mgr.print_active_memories()

    # =========================================================
    # Summary
    # =========================================================
    print_section("Summary")
    print("\n✅ What happened:")
    print("   1. Day 1: System learned 'user likes Sushi Lang'")
    print("   2. Day 2: System detected semantic conflict via embeddings")
    print("   3. Old memory deprecated, new memory activated")
    print("\n💡 Key insight:")
    print("   Conflict detection works on MEANING, not keywords!")
    print("   Even if user said 'hates Sushi Lang' vs 'loves Bin Sushi',")
    print("   the system recognizes both as 'restaurant preferences'.")

    # Cleanup
    memory_mgr.close()
    if os.path.exists("demo_memory.db"):
        os.remove("demo_memory.db")
        print("\n🧹 Cleaned up demo database.")


if __name__ == "__main__":
    main()
