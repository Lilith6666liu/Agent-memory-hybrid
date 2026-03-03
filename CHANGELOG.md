# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-03-03

### Added
- **Semantic conflict detection** using embedding cosine similarity
- **LLM-powered topic extraction** in Scratchpad (replaces hardcoded topics)
- **Embedding generation** for all candidate memories
- **Semantic search API** (`MemoryManager.search_similar()`)
- **Full test suite** with pytest
- **CI/CD pipeline** with GitHub Actions
- **Type hints** throughout codebase
- **Bilingual README** (English + Chinese)
- **Contributing guidelines**
- **MIT License**

### Changed
- Complete refactor of conflict detection (removed hardcoded "寿司" matching)
- Modern Python packaging with `pyproject.toml`
- Improved code organization with clear module separation
- Enhanced `LLMClient` to support both chat and embeddings

### Removed
- Hardcoded keyword-based conflict detection
- `AgenticFileSystem` dataclass (replaced with SQLite-only storage)
- In-memory AFS storage (now fully SQLite-backed)

## [0.3.0] - Previous

### Added
- SQLite persistence for long-term memory
- LLM evaluation for candidate memories
- Basic AFS drawer structure
- Day/night mode simulation

### Notes
- This was the original "PoC" version with hardcoded logic
- Only supported Chinese keyword matching for conflict detection
