# VodPipeline Tests

This directory contains unit tests for the VodPipeline project.

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Run Tests with Coverage

```bash
python -m pytest tests/ --cov=bin --cov-report=html
```

### Run Specific Test File

```bash
python -m pytest tests/test_config.py -v
```

## Test Structure

- `test_config.py` - Tests for configuration module (config.py)
- `test_logging_utils.py` - Tests for logging utilities (utils/logging_utils.py)

## Adding New Tests

1. Create a new test file following the naming convention `test_*.py`
2. Import the module you want to test
3. Write test classes inheriting from `unittest.TestCase`
4. Name test methods starting with `test_`
5. Run tests to verify they pass before committing

## Continuous Integration

Tests are automatically run on every pull request via GitHub Actions (see `.github/workflows/build.yml`).
All tests must pass before a PR can be merged.
