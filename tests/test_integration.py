"""Integration tests for the full memory pipeline."""
import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock

from memory import (
    ScratchpadManager,
    CandidateManager,
    MemoryManager,
    Message,
)


class TestFullPipeline:
    """Test the complete memory pipeline end-to-end."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        os.unlink(path)

    @pytest.fixture
    def pipeline(self, temp_db):
        """Create full pipeline with mocked LLM."""
        with patch('memory.scratchpad.LLMClient') as mock_scratch_llm, \
             patch('memory.candidate.LLMClient') as mock_cand_llm:

            # Mock scratchpad LLM
            mock_scratch = MagicMock()
            mock_scratch.call_llm_json.return_value = {
                "topic": "food preferences",
                "summary": "user likes sushi"
            }
            mock_scratch_llm.return_value = mock_scratch

            # Mock candidate LLM
            mock_cand = MagicMock()
            mock_cand.call_llm_json.return_value = {
                "has_value": True,
                "drawer": "preferences",
                "extracted_content": "user likes sushi",
                "confidence": 0.9
            }
            mock_cand.get_embedding.return_value = [1.0, 0.0, 0.0]
            mock_cand_llm.return_value = mock_cand

            scratchpad = ScratchpadManager(aggregation_threshold=2)
            candidate_mgr = CandidateManager()
            memory_mgr = MemoryManager(db_path=temp_db)

            yield scratchpad, candidate_mgr, memory_mgr
            memory_mgr.close()

    def test_full_pipeline_basic_flow(self, pipeline):
        """Test basic message → STM → candidate → memory flow."""
        scratchpad, candidate_mgr, memory_mgr = pipeline

        # Simulate conversation
        messages = [
            Message(role="user", content="I love sushi", msg_id="1"),
            Message(role="user", content="It's so delicious", msg_id="2"),
        ]

        for msg in messages:
            scratchpad.add_message(msg)

        # Aggregate
        stm = scratchpad.trigger_aggregation()
        assert stm is not None
        assert stm.topic == "food preferences"

        # Evaluate
        candidate = candidate_mgr.evaluate_stm(stm)
        assert candidate is not None
        assert candidate.target_drawer == "preferences"
        assert candidate.embedding is not None

        # Store
        memory_mgr.enqueue_candidate(candidate)
        stats = memory_mgr.run_sleep_update()
        assert stats["inserted"] == 1

        # Verify
        memories = memory_mgr.get_active_memories()
        assert len(memories) == 1
        assert "sushi" in memories[0]["content"]

    def test_pipeline_with_meaningless_filtering(self, pipeline):
        """Test that filler words are filtered out."""
        scratchpad, candidate_mgr, memory_mgr = pipeline

        # Mix of meaningful and meaningless
        messages = [
            Message(role="user", content="嗯", msg_id="1"),  # filtered
            Message(role="user", content="I love ramen", msg_id="2"),
            Message(role="user", content="OK", msg_id="3"),  # filtered
            Message(role="user", content="It's my favorite food", msg_id="4"),
        ]

        for msg in messages:
            scratchpad.add_message(msg)

        # Only 2 meaningful messages, need 2 for aggregation
        stm = scratchpad.trigger_aggregation()
        assert stm is not None
        # Should only include meaningful messages
        assert "嗯" not in stm.summary
        assert "OK" not in stm.summary
