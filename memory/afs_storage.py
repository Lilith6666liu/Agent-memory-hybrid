# memory/afs_storage.py
"""
Stage 3: Long-term Memory Storage (OpenViking AFS + LightMem hybrid)

Features:
  - SQLite persistence with embeddings
  - Semantic conflict detection via cosine similarity
  - Version evolution (active → deprecated)
  - Async batch processing (sleep update)
"""
import uuid
import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Tuple
from .models import CandidateMemory, MemoryStatus
from .embedding_utils import find_most_similar


class MemoryManager:
    """Manages long-term memory with semantic conflict resolution."""

    def __init__(self, db_path: str = "agent_memory.db", conflict_threshold: float = 0.75):
        self.db_path = db_path
        self.conflict_threshold = conflict_threshold
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()
        self.candidate_queue: List[CandidateMemory] = []

    def _create_tables(self):
        """Initialize database schema with embedding support."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS afs_memory (
                id TEXT PRIMARY KEY,
                drawer TEXT NOT NULL,
                content TEXT NOT NULL,
                status TEXT NOT NULL,
                embedding TEXT,  -- JSON-encoded vector
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_drawer_status ON afs_memory(drawer, status)
        ''')
        self.conn.commit()

    def enqueue_candidate(self, candidate: CandidateMemory) -> None:
        """Queue a candidate for async processing."""
        self.candidate_queue.append(candidate)

    def run_sleep_update(self) -> Dict[str, int]:
        """Process queued candidates: detect conflicts, evolve versions.

        Returns:
            stats dict with counts of inserted, updated, deprecated
        """
        stats = {"inserted": 0, "deprecated": 0}
        now = datetime.now().isoformat()
        cursor = self.conn.cursor()

        for candidate in self.candidate_queue:
            drawer = candidate.target_drawer

            # Fetch active memories in same drawer with embeddings
            cursor.execute(
                "SELECT id, content, embedding FROM afs_memory WHERE drawer = ? AND status = ?",
                (drawer, MemoryStatus.ACTIVE.value)
            )
            active_items = cursor.fetchall()

            # Prepare candidates for similarity search
            similarity_candidates = []
            for item_id, _, emb_json in active_items:
                if emb_json:
                    try:
                        emb = json.loads(emb_json)
                        similarity_candidates.append((item_id, emb))
                    except json.JSONDecodeError:
                        continue

            # Semantic conflict detection
            conflict_id = None
            if candidate.embedding and similarity_candidates:
                conflict_id, score = find_most_similar(
                    candidate.embedding,
                    similarity_candidates,
                    self.conflict_threshold
                )

            # Deprecate conflicting memory if found
            if conflict_id:
                cursor.execute(
                    "UPDATE afs_memory SET status = ?, updated_at = ? WHERE id = ?",
                    (MemoryStatus.DEPRECATED.value, now, conflict_id)
                )
                stats["deprecated"] += 1

            # Insert new memory
            new_id = str(uuid.uuid4())
            emb_json = json.dumps(candidate.embedding) if candidate.embedding else None
            cursor.execute(
                """INSERT INTO afs_memory
                   (id, drawer, content, status, embedding, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (new_id, drawer, candidate.content, MemoryStatus.ACTIVE.value,
                 emb_json, now, now)
            )
            stats["inserted"] += 1

        self.conn.commit()
        self.candidate_queue.clear()
        return stats

    def get_active_memories(self, drawer: Optional[str] = None) -> List[Dict]:
        """Retrieve active memories, optionally filtered by drawer."""
        cursor = self.conn.cursor()
        if drawer:
            cursor.execute(
                "SELECT id, drawer, content, created_at FROM afs_memory WHERE drawer = ? AND status = ? ORDER BY created_at DESC",
                (drawer, MemoryStatus.ACTIVE.value)
            )
        else:
            cursor.execute(
                "SELECT id, drawer, content, created_at FROM afs_memory WHERE status = ? ORDER BY drawer, created_at DESC",
                (MemoryStatus.ACTIVE.value,)
            )

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "drawer": row[1],
                "content": row[2],
                "created_at": row[3]
            })
        return results

    def search_similar(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Semantic search across all active memories."""
        from .embedding_utils import cosine_similarity

        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, drawer, content, embedding FROM afs_memory WHERE status = ?",
            (MemoryStatus.ACTIVE.value,)
        )

        scored = []
        for row in cursor.fetchall():
            emb_json = row[3]
            if not emb_json:
                continue
            try:
                emb = json.loads(emb_json)
                score = cosine_similarity(query_embedding, emb)
                scored.append((score, row[0], row[1], row[2]))
            except json.JSONDecodeError:
                continue

        scored.sort(reverse=True)
        return [
            {"id": sid, "drawer": drawer, "content": content, "score": score}
            for score, sid, drawer, content in scored[:top_k]
        ]

    def print_active_memories(self) -> None:
        """Pretty-print active memories grouped by drawer."""
        memories = self.get_active_memories()
        if not memories:
            print("\n[AFS] No active long-term memories.")
            return

        print(f"\n{'='*20} AFS Active Memories {'='*20}")
        current_drawer = None
        for m in memories:
            if m["drawer"] != current_drawer:
                print(f"\n📂 [{m['drawer']}]")
                current_drawer = m["drawer"]
            print(f"  - {m['content'][:60]}... ({m['created_at'][:10]})")
        print(f"\n{'='*60}")

    def close(self):
        """Close database connection."""
        self.conn.close()
