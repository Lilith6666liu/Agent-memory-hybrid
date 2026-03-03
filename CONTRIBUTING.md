# Contributing to Agent Memory Hybrid

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Lilith6666liu/Agent-memory-hybrid.git
   cd Agent-memory-hybrid
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Code Style

We use:
- **Black** for code formatting
- **Ruff** for linting
- **MyPy** for type checking

Run all checks before committing:
```bash
black memory tests
ruff check memory tests
mypy memory
```

## Testing

Run the test suite:
```bash
pytest
```

With coverage:
```bash
pytest --cov=memory --cov-report=html
```

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, documented code
   - Add tests for new functionality
   - Update documentation if needed

3. **Run quality checks**
   ```bash
   black --check memory tests
   ruff check memory tests
   mypy memory
   pytest
   ```

4. **Commit with clear messages**
   ```bash
   git commit -m "feat: add semantic search API"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Commit Message Convention

We follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Adding or updating tests
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Maintenance tasks

## Code Review

All PRs require:
- CI checks to pass
- At least one review approval
- No merge conflicts

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Documentation improvements
- General questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
