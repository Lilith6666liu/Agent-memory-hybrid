# memory/models.py
"""
Core data models for the Agent Memory Hybrid system.

Four-layer architecture:
  History → Scratchpad (STM) → Candidate → Memory (LTM/AFS)
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum


# ==========================================
# Enums
# ==========================================
class MemoryStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class DrawerType(str, Enum):
    """AFS drawer categories (extensible)."""
    PROFILE = "profile"           # Who the user is
    PREFERENCES = "preferences"   # What the user likes
    ENTITIES = "entities"         # People / things mentioned often
    EVENTS = "events"             # Key events
    CASES = "cases"               # Typical cases (agent-side)
    PATTERNS = "patterns"         # Reusable patterns (agent-side)


# ==========================================
# History Layer
# ==========================================
@dataclass
class Message:
    """A single raw conversation message."""
    role: str               # 'user' or 'assistant'
    content: str            # message text
    msg_id: str             # unique id
    timestamp: datetime = field(default_factory=datetime.now)
    is_meaningful: bool = True


# ==========================================
# Scratchpad Layer (Short-Term Memory)
# ==========================================
@dataclass
class ShortTermMemory:
    """An aggregated context block produced by the Scratchpad.

    Inspired by LightMem's Working Memory concept — bundle related
    messages into a coherent chunk to avoid fragmentation.
    """
    topic: str                      # extracted topic, e.g. "restaurant preference"
    summary: str                    # condensed summary
    source_msg_ids: List[str]       # traceable source messages
    created_at: datetime = field(default_factory=datetime.now)


# ==========================================
# Candidate Layer
# ==========================================
@dataclass
class CandidateMemory:
    """A memory candidate that passed LLM evaluation and awaits AFS commit.

    Fields:
        content:        core knowledge extracted, e.g. "user prefers sushi at Hin"
        target_drawer:  which AFS drawer it belongs to
        confidence:     LLM-assigned confidence (0-1)
        embedding:      dense vector for semantic conflict detection
        source_stm:     the STM it originated from
    """
    content: str
    target_drawer: str
    confidence: float
    source_stm: ShortTermMemory
    embedding: Optional[List[float]] = None


# ==========================================
# Long-Term Memory Layer (AFS)
# ==========================================
@dataclass
class MemoryItem:
    """A single record in the Agentic File System, with version tracking."""
    item_id: str
    drawer: str
    content: str
    status: MemoryStatus
    embedding: Optional[List[float]]
    created_at: datetime
    updated_at: datetime
