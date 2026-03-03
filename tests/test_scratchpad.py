"""Tests for ScratchpadManager."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from memory.scratchpad import ScratchpadManager
from memory.models import Message


class TestScratchpadManager:
    """Test scratchpad functionality."""

    @pytest.fixture
    def manager(self):
        """Create a ScratchpadManager with mocked LLM."""
        with patch('memory.scratchpad.LLMClient') as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.call_llm_json.return_value = {"topic": "test", "summary": "test summary"}
            mock_llm_class.return_value = mock_llm
            yield ScratchpadManager()

    def test_filters_meaningless_words(self, manager):
        """Should mark filler words as not meaningful."""
        msg = Message(role="user", content="嗯", msg_id="1")
        manager.add_message(msg)
        assert not msg.is_meaningful

    def test_keeps_meaningful_content(self, manager):
        """Should keep meaningful messages."""
        msg = Message(role="user", content="I love sushi", msg_id="1")
        manager.add_message(msg)
        assert msg.is_meaningful

    def test_no_aggregation_below_threshold(self, manager):
        """Should not aggregate if below threshold."""
        manager.aggregation_threshold = 3
        manager.add_message(Message(role="user", content="msg1", msg_id="1"))
        manager.add_message(Message(role="user", content="msg2", msg_id="2"))
        result = manager.trigger_aggregation()
        assert result is None

    def test_aggregation_creates_stm(self, manager):
        """Should create STM when threshold is met."""
        manager.aggregation_threshold = 2
        manager.llm_client.call_llm_json.return_value = {
            "topic": "food preferences",
            "summary": "user likes sushi"
        }
        manager.add_message(Message(role="user", content="I love sushi", msg_id="1"))
        manager.add_message(Message(role="user", content="It's my favorite", msg_id="2"))
        result = manager.trigger_aggregation()
        assert result is not None
        assert result.topic == "food preferences"
        assert result.summary == "user likes sushi"

    def test_tracks_aggregated_ids(self, manager):
        """Should track which messages have been aggregated."""
        manager.aggregation_threshold = 1
        msg = Message(role="user", content="test", msg_id="1")
        manager.add_message(msg)
        manager.trigger_aggregation()
        assert "1" in manager.aggregated_msg_ids
