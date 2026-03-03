"""Tests for embedding utility functions."""
import pytest
from memory.embedding_utils import cosine_similarity, find_most_similar


class TestCosineSimilarity:
    """Test cosine similarity computation."""

    def test_identical_vectors(self):
        """Similarity of identical vectors should be 1.0."""
        v = [1.0, 2.0, 3.0]
        assert cosine_similarity(v, v) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        """Similarity of orthogonal vectors should be 0.0."""
        a = [1.0, 0.0, 0.0]
        b = [0.0, 1.0, 0.0]
        assert cosine_similarity(a, b) == pytest.approx(0.0)

    def test_opposite_vectors(self):
        """Similarity of opposite vectors should be -1.0."""
        a = [1.0, 2.0, 3.0]
        b = [-1.0, -2.0, -3.0]
        assert cosine_similarity(a, b) == pytest.approx(-1.0)

    def test_empty_vectors(self):
        """Empty vectors should return 0.0."""
        assert cosine_similarity([], []) == 0.0

    def test_different_lengths(self):
        """Vectors of different lengths should return 0.0."""
        assert cosine_similarity([1.0, 2.0], [1.0, 2.0, 3.0]) == 0.0


class TestFindMostSimilar:
    """Test finding most similar candidate."""

    def test_finds_best_match(self):
        """Should return the most similar candidate above threshold."""
        query = [1.0, 0.0, 0.0]
        candidates = [
            ("id1", [0.9, 0.1, 0.0]),  # very similar
            ("id2", [0.0, 1.0, 0.0]),  # orthogonal
            ("id3", [0.5, 0.5, 0.0]),  # somewhat similar
        ]
        best_id, score = find_most_similar(query, candidates, threshold=0.7)
        assert best_id == "id1"
        assert score > 0.9

    def test_no_match_below_threshold(self):
        """Should return None if no candidate meets threshold."""
        query = [1.0, 0.0, 0.0]
        candidates = [
            ("id1", [0.0, 1.0, 0.0]),  # orthogonal
        ]
        best_id, score = find_most_similar(query, candidates, threshold=0.7)
        assert best_id is None
        assert score == 0.0

    def test_empty_candidates(self):
        """Should handle empty candidate list."""
        best_id, score = find_most_similar([1.0, 0.0], [], threshold=0.5)
        assert best_id is None
        assert score == 0.0
