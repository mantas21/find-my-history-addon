# Testing Strategy for Find My History Add-on

## Document Information
- **Version**: 1.0
- **Last Updated**: 2025-01-27
- **Application**: Find My History - Home Assistant Add-on
- **Tech Stack**: Python 3, aiohttp, InfluxDB, Home Assistant API

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Testing Objectives](#testing-objectives)
3. [Application Overview](#application-overview)
4. [Test Levels & Types](#test-levels--types)
5. [Test Scope](#test-scope)
6. [Test Environment Strategy](#test-environment-strategy)
7. [Test Data Management](#test-data-management)
8. [Test Automation Strategy](#test-automation-strategy)
9. [Test Tools & Frameworks](#test-tools--frameworks)
10. [Test Execution Plan](#test-execution-plan)
11. [Risk Assessment](#risk-assessment)
12. [Success Criteria](#success-criteria)

---

## Executive Summary

This document outlines a comprehensive testing strategy for the Find My History Home Assistant add-on. The strategy covers unit, integration, and end-to-end testing with emphasis on mocking external dependencies (Home Assistant API and InfluxDB).

**Key Highlights:**
- Unit tests for core logic (zone detection, data processing)
- Integration tests with mocked Home Assistant and InfluxDB clients
- API endpoint testing
- Coverage target: 80%+ for core modules

---

## Testing Objectives

### Primary Objectives
1. **Functional Correctness**: Ensure all features work as specified
2. **Zone Detection Accuracy**: Validate Haversine formula calculations
3. **API Reliability**: Ensure all API endpoints work correctly
4. **Data Integrity**: Verify location data is stored and retrieved correctly
5. **Error Handling**: Validate graceful handling of failures
6. **Performance**: Ensure polling and API responses are efficient

### Secondary Objectives
1. **Maintainability**: Establish automated test suite for regression prevention
2. **Documentation**: Create test documentation for future reference
3. **CI/CD Integration**: Automate test execution in GitHub Actions

---

## Application Overview

### Application Architecture
- **Backend**: Python 3 with aiohttp
- **Database**: InfluxDB 1.x and 2.x compatible
- **External APIs**: Home Assistant REST API
- **Frontend**: Vanilla JavaScript with Leaflet.js (separate testing)

### Key Modules
1. **`zone_detector.py`**: Zone detection using Haversine formula
2. **`ha_client.py`**: Home Assistant API client
3. **`influxdb_client.py`**: InfluxDB read/write operations
4. **`api.py`**: REST API endpoints
5. **`main.py`**: Main polling service
6. **`device_prefs.py`**: Device preference management
7. **`log_utils.py`**: Logging utilities

### API Endpoints
- `GET /api/health` - Health check
- `GET /api/devices` - List all device trackers
- `GET /api/zones` - List Home Assistant zones
- `GET /api/locations` - Get location history
- `GET /api/stats` - Get statistics
- `POST /api/devices/toggle` - Toggle device tracking
- `POST /api/devices/update` - Force location update

---

## Test Levels & Types

### 1. Unit Testing

**Scope**: Individual functions and classes

**Coverage Targets**:
- Core logic modules: 90%+ coverage
- Client modules: 85%+ coverage
- API modules: 80%+ coverage

**Key Areas**:

#### ZoneDetector Tests
- Haversine distance calculation accuracy
- Zone detection with various radius values
- Edge cases (no zones, invalid coordinates)
- Zone radius parsing (string vs number)

#### HomeAssistantClient Tests
- API request construction
- Error handling
- Response parsing
- Device tracker filtering

#### InfluxDBLocationClient Tests
- Connection initialization (1.x vs 2.x)
- Location data writing
- Location data querying
- Error handling

#### DevicePrefs Tests
- Preference loading
- Preference saving
- Default values

#### LogUtils Tests
- Coordinate formatting
- Secure logging configuration

### 2. Integration Testing

**Scope**: Module interactions with mocked dependencies

**Coverage Targets**:
- API endpoints: 100% coverage
- Main polling service: Critical paths

**Key Areas**:
- API server with mocked HA and InfluxDB clients
- Main service with mocked dependencies
- End-to-end data flow (HA → Zone Detection → InfluxDB)

### 3. API Testing

**Scope**: HTTP API endpoints

**Coverage Targets**:
- All endpoints: 100% coverage
- Error scenarios: All error codes

**Key Areas**:
- Request/response validation
- CORS headers
- Error responses
- Query parameters
- Request body validation

### 4. End-to-End Testing

**Scope**: Full system with test containers (optional)

**Coverage Targets**:
- Critical user journeys: 100%

**Key Areas**:
- Device polling workflow
- Location storage and retrieval
- Zone detection in real scenarios
- API endpoint functionality

---

## Test Scope

### In Scope

✅ **Backend Testing**
- All Python modules
- API endpoints
- Zone detection logic
- Data processing
- Error handling

✅ **Integration Testing**
- Module interactions
- API with mocked dependencies
- Data flow validation

### Out of Scope

❌ **Frontend Testing**
- JavaScript/Leaflet.js (separate testing strategy)
- UI components (manual testing)

❌ **Infrastructure**
- Docker container testing
- Home Assistant integration testing
- Production deployment testing

---

## Test Environment Strategy

### Environments

1. **Local Development**
   - Purpose: Unit and integration testing
   - Dependencies: Mocked (pytest-mock, responses)
   - Data: Test fixtures

2. **CI/CD (GitHub Actions)**
   - Purpose: Automated test execution
   - Dependencies: Mocked
   - Data: Test fixtures

3. **Staging (Optional)**
   - Purpose: Integration with real services
   - Dependencies: Test Home Assistant instance, test InfluxDB
   - Data: Test data

---

## Test Data Management

### Test Fixtures

1. **Zone Data**
   - Valid zones with coordinates and radius
   - Edge cases (no radius, invalid coordinates)
   - Multiple zones

2. **Device Tracker Data**
   - Valid device states
   - Missing location data
   - Various battery levels

3. **Location Data**
   - Valid coordinates
   - Edge cases (poles, equator)
   - Historical location data

4. **API Responses**
   - Successful responses
   - Error responses
   - Empty responses

---

## Test Automation Strategy

### Automation Pyramid

```
        /\
       /E2E\          (10%) - Full system tests (optional)
      /------\
     /Integration\   (30%) - Module interactions
    /------------\
   /   Unit Tests  \  (60%) - Individual functions
  /----------------\
```

### Automation Priorities

**Phase 1: Foundation (Week 1)**
- Unit tests for `zone_detector.py`
- Unit tests for `log_utils.py`
- Unit tests for `device_prefs.py`

**Phase 2: Core Features (Week 2)**
- Unit tests for `ha_client.py` (mocked)
- Unit tests for `influxdb_client.py` (mocked)
- Integration tests for API endpoints

**Phase 3: Comprehensive (Week 3)**
- Integration tests for main polling service
- API endpoint tests
- Error handling tests

---

## Test Tools & Frameworks

### Recommended Tool Stack

#### Testing Framework
- **pytest**: Test runner and framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking utilities

#### Mocking Libraries
- **responses**: Mock HTTP requests
- **unittest.mock**: Python mocking
- **aioresponses**: Async HTTP mocking

#### Code Quality
- **pylint**: Code linting
- **black**: Code formatting
- **mypy**: Type checking

### Installation

```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock responses aioresponses
pip install pylint black mypy
```

---

## Test Execution Plan

### Test Phases

#### Phase 1: Unit Testing (Week 1)
- **Duration**: 1 week
- **Focus**: Core logic modules
- **Deliverable**: 80%+ unit test coverage
- **Owner**: Development team

#### Phase 2: Integration Testing (Week 2)
- **Duration**: 1 week
- **Focus**: API endpoints, module interactions
- **Deliverable**: All API endpoints tested
- **Owner**: Development team

#### Phase 3: Comprehensive Testing (Week 3)
- **Duration**: 1 week
- **Focus**: Error handling, edge cases
- **Deliverable**: Complete test suite
- **Owner**: Development team

---

## Risk Assessment

### High Risk Areas

1. **Zone Detection Accuracy**
   - **Risk**: Incorrect zone detection
   - **Mitigation**: Comprehensive unit tests with known coordinates
   - **Priority**: Critical

2. **Data Loss**
   - **Risk**: Location data not stored correctly
   - **Mitigation**: Integration tests with mocked InfluxDB
   - **Priority**: High

3. **API Reliability**
   - **Risk**: API endpoints fail
   - **Mitigation**: Full API test coverage
   - **Priority**: High

### Medium Risk Areas

- Home Assistant API integration
- InfluxDB connection handling
- Error recovery

---

## Success Criteria

### Test Coverage Metrics

- **Unit Test Coverage**: ≥ 80%
- **Integration Test Coverage**: 100% of API endpoints
- **Critical Path Coverage**: 100%

### Quality Gates

**Before Release:**
- ✅ All critical bugs fixed
- ✅ All unit tests passing
- ✅ All integration tests passing
- ✅ Coverage targets met
- ✅ No critical security issues

---

## Appendix

### Test Directory Structure

```
tests/
├── docs/                    # Testing documentation
├── unit/                    # Unit tests
│   ├── test_zone_detector.py
│   ├── test_ha_client.py
│   ├── test_influxdb_client.py
│   ├── test_device_prefs.py
│   └── test_log_utils.py
├── integration/            # Integration tests
│   ├── test_api.py
│   └── test_main.py
├── e2e/                    # End-to-end tests (optional)
├── fixtures/               # Test data
│   ├── zones.json
│   ├── device_trackers.json
│   └── locations.json
├── conftest.py            # Pytest configuration
└── pytest.ini            # Pytest settings
```

---

**Document Status**: Draft  
**Next Review Date**: [To be scheduled]
