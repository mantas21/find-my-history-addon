# Testing Quick Start Guide

Get started with testing in 5 minutes!

## Step 1: Install Dependencies

```bash
cd /Users/mmazuna/Projects/find-my-history-addon-clean
pip install -r tests/requirements.txt
```

## Step 2: Run Your First Test

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/unit/test_zone_detector.py -v

# Run with coverage
pytest tests/ --cov=find_my_history_addon/find_my_history --cov-report=term-missing
```

## Step 3: View Test Results

Tests will show:
- ✅ Passing tests
- ❌ Failing tests
- Coverage percentage
- Test execution time

## Common Commands

```bash
# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run tests matching a pattern
pytest tests/ -k "zone"

# Run tests with verbose output
pytest tests/ -v

# Run tests and stop on first failure
pytest tests/ -x

# Run tests in parallel (if pytest-xdist installed)
pytest tests/ -n auto
```

## Next Steps

1. Read [TESTING_STRATEGY.md](./docs/TESTING_STRATEGY.md) for full strategy
2. Check [README.md](./README.md) for detailed documentation
3. Write your first test in `tests/unit/`
4. Run tests before committing code

## Need Help?

- Check test examples in `tests/unit/`
- Review fixtures in `conftest.py`
- See [TESTING_STRATEGY.md](./docs/TESTING_STRATEGY.md) for detailed guidance
