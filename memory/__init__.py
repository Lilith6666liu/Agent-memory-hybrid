"""
Agent Memory Hybrid - A semantic memory system for AI agents.

Combines OpenViking's AFS drawer structure with LightMem's async processing,
with modern embedding-based conflict detection.

Basic usage:
    from memory import ScratchpadManager, CandidateManager, MemoryManager

    scratchpad = ScratchpadManager()
    candidate_mgr = CandidateManager()
    memory_mgr = MemoryManager()

    # Add messages...
    scratchpad.add_message(Message(role="user", content="...", msg_id="1"))

    # Aggregate into STM
    stm = scratchpad.trigger_aggregation()

    # Evaluate and queue
    if stm:
        candidate = candidate_mgr.evaluate_stm(stm)
        if candidate:
            memory_mgr.enqueue_candidate(candidate)

    # Batch process (sleep update)
    stats = memory_mgr.run_sleep_update()
"""

from .models import (
    Message,
    ShortTermMemory,
    CandidateMemory,
    MemoryItem,
    MemoryStatus,
    DrawerType,
)
from .scratchpad import ScratchpadManager
from .candidate import CandidateManager
from .afs_storage import MemoryManager
from .llm_client import LLMClient
from .embedding_utils import cosine_similarity, find_most_similar

__version__ = "0.4.0"
__all__ = [
    "Message",
    "ShortTermMemory",
    "CandidateMemory",
    "MemoryItem",
    "MemoryStatus",
    "DrawerType",
    "ScratchpadManager",
    "CandidateManager",
    "MemoryManager",
    "LLMClient",
    "cosine_similarity",
    "find_most_similar",
]
