# memory/embedding_utils.py
"""
Utility functions for embedding-based semantic operations.
"""
import math
from typing import List


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def find_most_similar(
    query: List[float],
    candidates: List[tuple],
    threshold: float = 0.75
) -> tuple:
    """Find the most similar candidate above threshold.

    Args:
        query: embedding vector
        candidates: list of (id, embedding) tuples
        threshold: minimum similarity to consider a match

    Returns:
        (best_id, best_score) or (None, 0.0) if none above threshold
    """
    best_id = None
    best_score = 0.0

    for cid, emb in candidates:
        score = cosine_similarity(query, emb)
        if score > best_score and score >= threshold:
            best_score = score
            best_id = cid

    return best_id, best_score
