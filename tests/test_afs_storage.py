"""Tests for MemoryManager (AFS storage)."""
import os
import pytest
import tempfile
from memory.afs_storage import MemoryManager
from memory.models import CandidateMemory, ShortTermMemory, MemoryStatus


class TestMemoryManager:
    """Test AFS storage functionality."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        os.unlink(path)

    @pytest.fixture
    def manager(self, temp_db):
        """Create a MemoryManager with temp database."""
        mgr = MemoryManager(db_path=temp_db, conflict_threshold=0.8)
        yield mgr
        mgr.close()

    @pytest.fixture
    def sample_candidate(self):
        """Create a sample candidate memory."""
        stm = ShortTermMemory(
            topic="food",
            summary="user likes pizza",
            source_msg_ids=["1"]
        )
        return CandidateMemory(
            content="user likes pizza",
            target_drawer="preferences",
            confidence=0.9,
            source_stm=stm,
            embedding=[1.0, 0.0, 0.0]
        )

    def test_enqueue_candidate(self, manager, sample_candidate):
        """Should queue candidates for processing."""
        manager.enqueue_candidate(sample_candidate)
        assert len(manager.candidate_queue) == 1

    def test_sleep_update_inserts_memory(self, manager, sample_candidate):
        """Should insert memory on sleep update."""
        manager.enqueue_candidate(sample_candidate)
        stats = manager.run_sleep_update()
        assert stats["inserted"] == 1
        assert stats["deprecated"] == 0

    def test_retrieves_active_memories(self, manager, sample_candidate):
        """Should retrieve active memories."""
        manager.enqueue_candidate(sample_candidate)
        manager.run_sleep_update()
        memories = manager.get_active_memories()
        assert len(memories) == 1
        assert memories[0]["content"] == "user likes pizza"

    def test_filters_by_drawer(self, manager):
        """Should filter memories by drawer."""
        stm = ShortTermMemory(topic="test", summary="test", source_msg_ids=["1"])
        c1 = CandidateMemory("content1", "preferences", 0.9, stm, [1.0, 0.0])
        c2 = CandidateMemory("content2", "profile", 0.9, stm, [0.0, 1.0])
        manager.enqueue_candidate(c1)
        manager.enqueue_candidate(c2)
        manager.run_sleep_update()

        pref_memories = manager.get_active_memories(drawer="preferences")
        assert len(pref_memories) == 1
        assert pref_memories[0]["drawer"] == "preferences"

    def test_semantic_conflict_detection(self, manager):
        """Should detect conflicts via embedding similarity."""
        stm = ShortTermMemory(topic="food", summary="test", source_msg_ids=["1"])
        # First memory
        c1 = CandidateMemory("user likes pizza", "preferences", 0.9, stm, [1.0, 0.0, 0.0])
        manager.enqueue_candidate(c1)
        manager.run_sleep_update()

        # Similar memory (should conflict)
        c2 = CandidateMemory("user prefers pasta", "preferences", 0.9, stm, [0.95, 0.1, 0.0])
        manager.enqueue_candidate(c2)
        stats = manager.run_sleep_update()

        assert stats["deprecated"] == 1  # old one deprecated
        assert stats["inserted"] == 1    # new one inserted

        # Check old is deprecated
        cursor = manager.conn.cursor()
        cursor.execute("SELECT status FROM afs_memory WHERE content = ?", ("user likes pizza",))
        result = cursor.fetchone()
        assert result[0] == MemoryStatus.DEPRECATED.value
