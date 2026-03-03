# memory/scratchpad.py
"""
Stage 1: Scratchpad Manager (LightMem-inspired)

Responsibilities:
  1. Entry filtering — drop meaningless filler words.
  2. Topic aggregation — bundle messages into coherent STM chunks.
  3. LLM-powered topic extraction — no more hard-coded placeholders.
"""
from typing import List, Optional
from .models import Message, ShortTermMemory
from .llm_client import LLMClient


class ScratchpadManager:
    """Manages the short-term working memory."""

    # Common filler words to filter out
    MEANINGLESS_WORDS = {
        "嗯", "好的", "没问题", "哦", "哈喽", "你好", "哈", "呵",
        "嗯嗯", "好的呢", "收到", "OK", "ok", "了解", "知道了",
        "thanks", "thank you", "ok", "okay", "sure", "got it"
    }

    def __init__(self, aggregation_threshold: int = 3):
        self.raw_history: List[Message] = []
        self.short_term_memories: List[ShortTermMemory] = []
        self.aggregated_msg_ids: set = set()
        self.aggregation_threshold = aggregation_threshold
        self.llm_client = LLMClient()

    def add_message(self, message: Message) -> None:
        """Add a message with lightweight entry filtering."""
        cleaned = message.content.strip().rstrip("!！?？.。~")
        if cleaned in self.MEANINGLESS_WORDS or len(cleaned) < 2:
            message.is_meaningful = False
        self.raw_history.append(message)

    def trigger_aggregation(self) -> Optional[ShortTermMemory]:
        """Bundle pending messages into an STM chunk using LLM topic extraction."""
        pending = [
            m for m in self.raw_history
            if m.is_meaningful and m.msg_id not in self.aggregated_msg_ids
        ]

        if len(pending) < self.aggregation_threshold:
            return None

        batch = pending[:self.aggregation_threshold]
        combined = " | ".join([m.content for m in batch])

        # Use LLM to extract topic and generate summary
        topic, summary = self._extract_topic_with_llm(combined)

        stm = ShortTermMemory(
            topic=topic,
            summary=summary,
            source_msg_ids=[m.msg_id for m in batch]
        )

        self.short_term_memories.append(stm)
        for m in batch:
            self.aggregated_msg_ids.add(m.msg_id)

        return stm

    def _extract_topic_with_llm(self, text: str) -> tuple[str, str]:
        """Use LLM to extract topic and summary from aggregated text."""
        prompt = f"""You are a conversation analyst. Given the following aggregated messages, extract:
1. A concise topic (3-5 words max)
2. A one-sentence summary

Messages: {text}

Return ONLY a JSON object in this exact format:
{{"topic": "...", "summary": "..."}}"""

        result = self.llm_client.call_llm_json(prompt)
        if result:
            return result.get("topic", "general"), result.get("summary", text[:100])
        return "general", text[:100]
