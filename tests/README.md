# Test Organization

This test suite is organized into three distinct categories to clearly separate concerns and testing scopes.

## Directory Structure

```
tests/
├── unit/           # Unit tests - fast, isolated, no external dependencies
├── integration/    # Integration tests - test component interactions
├── e2e/           # End-to-end tests - test complete workflows
└── conftest.py    # Shared fixtures
```

## Test Categories

### Unit Tests (`tests/unit/`)
**Purpose**: Test individual functions and classes in isolation

**Characteristics**:
- Fast execution (< 100ms per test)
- No external dependencies (no TestClient, no FastAPI app startup)
- Mock external interactions
- Focus on single functions/methods

**Examples**:
- `test_utils.py` - Utility function tests
- `test_schemas.py` - Pydantic model validation
- `test_config.py` - Configuration parsing
- `test_apscheduler_builder.py` - Builder logic
- `test_router_deps.py` - Dependency injection

**Run**: `pytest -m unit`

### Integration Tests (`tests/integration/`)
**Purpose**: Test how our components integrate with FastAPI and APScheduler

**Characteristics**:
- Test FastAPI routers with TestClient
- Test API endpoints (HTTP layer)
- Verify request/response serialization
- Test pagination, error handling, status codes
- Focus on our wrapper code, not APScheduler internals

**Examples**:
- `test_router_tasks.py` - Tasks API endpoint integration
- `test_router_schedules.py` - Schedules API endpoint integration
- `test_concurrent.py` - Concurrent API request handling
- `test_app.py` - App initialization and configuration
- `test_postgres.py` - PostgreSQL datastore integration

**Run**: `pytest -m integration`

### End-to-End Tests (`tests/e2e/`)
**Purpose**: Test complete workflows across multiple components

**Characteristics**:
- Test full user workflows (create → read → update → delete)
- Test multiple endpoints together
- Verify complete lifecycle (startup → operation → shutdown)
- Test real-world usage scenarios

**Examples**:
- `test_workflows.py`:
  - Full lifecycle workflow (scheduler start/stop)
  - CRUD workflow (create, read, update, delete schedules)
  - Task retrieval workflow
  - Pagination workflow
  - Error handling workflow
  - API response format workflow

**Run**: `pytest -m e2e`

## Running Tests

```bash
# Run all tests
pytest

# Run by category
pytest -m unit          # Fast unit tests only
pytest -m integration   # Integration tests only
pytest -m e2e          # End-to-end workflows only

# Run with coverage
pytest --cov=src/fastapi_apscheduler4

# Run specific test file
pytest tests/unit/test_utils.py
pytest tests/integration/test_router_tasks.py
pytest tests/e2e/test_workflows.py
```

## Test Patterns

### Arrange-Act-Assert (AAA)
All tests follow the AAA pattern:

```python
def test_example():
    # Arrange - Set up test data and expected values
    scheduler_app = SchedulerApp()
    expected_count = 2

    # Act - Execute the code under test
    with TestClient(app) as client:
        response = client.get("/api/v1/tasks")
        tasks = parse_tasks(response.text)

    # Assert - Verify the results
    assert response.status_code == 200
    assert len(tasks) == expected_count
```

### Fixtures
Common setup is extracted to fixtures in `conftest.py`:

```python
@pytest.fixture
def scheduler_app() -> SchedulerApp:
    """Provides a fresh SchedulerApp instance."""
    return SchedulerApp()
```

### Module-Level Task Functions
Task functions must be defined at module level (not nested) for APScheduler serialization:

```python
# ✓ Correct - module level
def my_task() -> None:
    """Task function."""
    pass

# ✗ Wrong - nested function
@pytest.fixture
def my_task() -> callable:
    def _task() -> None:
        pass
    return _task  # APScheduler cannot serialize this
```

## Test Coverage

Current coverage: **73 tests**

- **Unit**: 41 tests (fast, isolated logic)
- **Integration**: 21 tests (API layer, routers)
- **E2E**: 6 tests (complete workflows)

## Key Principles

1. **Unit tests** validate our logic in isolation
2. **Integration tests** verify our FastAPI wrapper works correctly
3. **E2E tests** ensure complete user workflows function end-to-end
4. **Don't test APScheduler** - only test our integration with it
5. **Use fixtures** to reduce duplication
6. **Follow AAA pattern** for clarity
7. **Name tests clearly** - describe what integration layer feature is being tested
