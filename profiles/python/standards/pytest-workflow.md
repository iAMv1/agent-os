# Pytest Workflow

## Test Organization
- Place tests in `tests/` directory mirroring source structure
- Name test files `test_<module>.py`
- Name test functions `test_<functionality>()`
- Use test classes for grouping related tests

## Test Structure
- Follow Arrange-Act-Assert pattern
- Use fixtures for setup and teardown
- Parametrize tests for multiple input cases
- Mock external dependencies with `unittest.mock`

## Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_module.py::test_function

# Run with verbose output
pytest -v
```

## Test Quality
- Test both happy path and edge cases
- Use descriptive test names that explain the scenario
- Keep tests independent and repeatable
- Aim for meaningful coverage, not just high numbers
