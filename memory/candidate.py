# memory/candidate.py
"""
Stage 2: Candidate Manager

Uses LLM to evaluate whether an STM chunk has long-term value,
assigns it to an AFS drawer, and generates an embedding for
semantic conflict detection.
"""
from typing import List, Optional
from .models import ShortTermMemory, CandidateMemory
from .llm_client import LLMClient


class CandidateManager:
    """Evaluates STM chunks and produces candidate memories."""

    def __init__(self):
        self.candidates: List[CandidateMemory] = []
        self.llm_client = LLMClient()

    def evaluate_stm(self, stm: ShortTermMemory) -> Optional[CandidateMemory]:
        """Evaluate STM and optionally produce a candidate with embedding."""
        prompt = f"""You are a memory curator. Analyze this conversation summary and decide:

Summary: {stm.summary}

1. Does it contain valuable personal info (profile, preferences, entities, events)?
2. If yes, extract the core fact (replace "I/me" with "user").
3. Assign the best drawer: profile, preferences, entities, events.
4. Assign confidence (0.0-1.0).

Return JSON:
{{"has_value": true/false, "drawer": "...", "extracted_content": "...", "confidence": 0.9}}"""

        result = self.llm_client.call_llm_json(prompt)
        if not result or not result.get("has_value"):
            return None

        content = result.get("extracted_content", stm.summary)
        drawer = result.get("drawer", "entities")
        confidence = result.get("confidence", 0.8)

        # Generate embedding for semantic conflict detection
        embedding = self.llm_client.get_embedding(content)

        candidate = CandidateMemory(
            content=content,
            target_drawer=drawer,
            confidence=confidence,
            source_stm=stm,
            embedding=embedding
        )
        self.candidates.append(candidate)
        return candidate
