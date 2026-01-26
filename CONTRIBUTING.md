# Contributing to fastapi-apscheduler4

Thank you for your interest in contributing to fastapi-apscheduler4!

## Development Setup

```bash
# Clone the repository
git clone https://github.com/grelinfo/fastapi-apscheduler4.git
cd fastapi-apscheduler4

# Install dependencies with uv
uv sync

# Install pre-commit hooks
pre-commit install
```

## Testing

### Test Organization

The test suite is organized into three categories:

```
tests/
├── unit/           # Fast, isolated tests (41 tests)
├── integration/    # Component interaction tests (21 tests)
└── e2e/           # Complete workflow tests (6 tests)
```

**Unit Tests** (`tests/unit/`):
- Test individual functions and classes in isolation
- Fast execution (< 100ms per test)
- No external dependencies
- Examples: utils, schemas, config validation

**Integration Tests** (`tests/integration/`):
- Test FastAPI router integration with APScheduler
- Verify API endpoints, pagination, error handling
- Focus on our wrapper code, not APScheduler internals
- Examples: router tests, concurrent operations

**End-to-End Tests** (`tests/e2e/`):
- Test complete workflows across multiple components
- Full lifecycle testing (startup → operation → shutdown)
- Examples: CRUD workflows, error handling workflows

### Running Tests

```bash
# Run all tests
pytest

# Run by category
pytest -m unit          # Fast unit tests only
pytest -m integration   # Integration tests only
pytest -m e2e          # End-to-end workflows only

# Run with coverage
pytest --cov=src/fastapi_apscheduler4

# Run specific file
pytest tests/unit/test_utils.py
```

### Test Patterns

All tests follow the **Arrange-Act-Assert (AAA)** pattern:

```python
@pytest.mark.unit
def test_example():
    # Arrange - Set up test data and expected values
    expected_count = 2

    # Act - Execute the code under test
    result = process_data(input_data)

    # Assert - Verify the results
    assert len(result) == expected_count
```

### Important Constraints

**Module-level task functions**: Task functions must be defined at module level (not nested) for APScheduler serialization:

```python
# ✓ Correct
def my_task() -> None:
    """Task function."""
    pass

# ✗ Wrong - APScheduler cannot serialize nested functions
@pytest.fixture
def my_task() -> callable:
    def _task() -> None:
        pass
    return _task
```

## Code Quality

```bash
# Run linter
ruff check .

# Format code
ruff format .

# Type checking
pyright
```

## Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes following conventional commits
6. Push to your fork
7. Open a Pull Request

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
```
feat: add support for Redis event broker
fix: correct pagination header calculation
test: add integration tests for schedule deletion
docs: update getting started guide
```

## Questions?

Feel free to open an issue for questions or discussions!
