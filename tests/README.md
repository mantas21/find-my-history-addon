# Testing Documentation

This directory contains all testing-related materials for the Find My History add-on.

## Directory Structure

```
tests/
├── docs/                    # Testing documentation
│   ├── TESTING_STRATEGY.md  # Main testing strategy
│   ├── TEST_IMPLEMENTATION_GUIDE.md  # Implementation guide
│   └── TESTING_CHECKLIST.md # Quick reference checklist
├── unit/                    # Unit tests
│   ├── test_zone_detector.py      # ✅ Zone detection tests
│   ├── test_log_utils.py          # ✅ Logging utility tests
│   ├── test_device_prefs.py       # ✅ Device preferences tests
│   ├── test_ha_client.py          # ✅ Home Assistant client tests
│   └── test_influxdb_client.py    # ✅ InfluxDB client tests
├── integration/            # Integration tests
│   └── test_api.py         # ✅ API endpoint tests
├── e2e/                    # End-to-end tests
│   ├── test_full_workflow.py  # ✅ Full workflow E2E tests
│   └── README.md           # E2E setup instructions
├── frontend/               # Frontend tests
│   ├── __tests__/
│   │   └── find-my-history-card.test.js  # ✅ Frontend tests
│   ├── package.json        # Frontend test dependencies
│   └── jest.setup.js       # Jest configuration
├── fixtures/               # Test data
│   ├── zones.json
│   └── device_trackers.json
├── conftest.py            # Pytest configuration and fixtures
├── pytest.ini            # Pytest settings
└── requirements.txt      # Testing dependencies
```

## Quick Start

### 1. Install Testing Dependencies

```bash
cd /Users/mmazuna/Projects/find-my-history-addon-clean
pip install -r tests/requirements.txt
```

### 2. Run Tests

```bash
# Run all tests
pytest tests/

# Run unit tests only
pytest tests/unit/

# Run with coverage
pytest tests/ --cov=find_my_history_addon/find_my_history --cov-report=html

# Run specific test file
pytest tests/unit/test_zone_detector.py

# Run with verbose output
pytest tests/ -v
```

### 3. View Coverage Report

After running tests with coverage:

```bash
# HTML report
open htmlcov/index.html

# Terminal report
pytest tests/ --cov=find_my_history_addon/find_my_history --cov-report=term-missing
```

## Test Categories

### Unit Tests (`tests/unit/`)

Test individual functions and classes in isolation:
- ✅ `test_zone_detector.py` - Zone detection logic (12 tests)
- ✅ `test_log_utils.py` - Logging utilities (4 tests)
- ✅ `test_device_prefs.py` - Device preferences (13 tests)
- ✅ `test_ha_client.py` - Home Assistant client (mocked, 10 tests)
- ✅ `test_influxdb_client.py` - InfluxDB client (mocked, 10 tests)

### Integration Tests (`tests/integration/`)

Test module interactions:
- `test_api.py` - API endpoints with mocked dependencies
- `test_main.py` - Main polling service

### End-to-End Tests (`tests/e2e/`)

Full system tests with real Home Assistant and InfluxDB instances:
- ✅ `test_full_workflow.py` - Complete workflow tests
- See `tests/e2e/README.md` for setup instructions

### Frontend Tests (`tests/frontend/`)

JavaScript/TypeScript tests for the frontend:
- ✅ `find-my-history-card.test.js` - Card component tests
- Uses Jest with jsdom environment
- See `tests/frontend/README.md` for details

## Writing Tests

### Example Unit Test

```python
"""Unit tests for zone_detector module."""

import pytest
from find_my_history.zone_detector import ZoneDetector

def test_check_zone_inside_radius(sample_zones):
    """Test zone detection when device is inside zone radius."""
    detector = ZoneDetector(sample_zones)
    in_zone, zone_name = detector.check_zone(54.8985, 23.9036)
    assert in_zone is True
    assert zone_name == "home"
```

### Example Integration Test

```python
"""Integration tests for API endpoints."""

import pytest
from aiohttp.test_utils import make_mocked_request

@pytest.mark.asyncio
async def test_health_endpoint(api_server):
    """Test health check endpoint."""
    request = make_mocked_request("GET", "/api/health")
    response = await api_server.app.router._resources[0]._handler(request)
    assert response.status == 200
```

## Test Fixtures

Common fixtures are defined in `conftest.py`:
- `sample_zones` - Sample Home Assistant zones
- `sample_device_trackers` - Sample device tracker states
- `sample_location_data` - Sample location data
- `mock_ha_client` - Mocked Home Assistant client
- `mock_influxdb_client` - Mocked InfluxDB client

## Coverage Goals

- **Unit Tests**: ≥ 80% coverage
- **Integration Tests**: 100% of API endpoints
- **Critical Paths**: 100% coverage

## CI/CD Integration

Tests are automatically run in GitHub Actions on:
- Push to main branch
- Pull requests
- Scheduled runs (optional)

See `.github/workflows/test.yml` for configuration.

## Troubleshooting

### Import Errors

If you get import errors, make sure you're running tests from the project root:

```bash
cd /Users/mmazuna/Projects/find-my-history-addon-clean
pytest tests/
```

### Async Test Issues

Make sure `pytest-asyncio` is installed and `asyncio_mode = auto` is set in `pytest.ini`.

### Mock Issues

For HTTP mocking, use `responses` for sync requests and `aioresponses` for async requests.

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Testing Strategy](./docs/TESTING_STRATEGY.md)
