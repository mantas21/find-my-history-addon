# End-to-End Testing

End-to-end tests require real Home Assistant and InfluxDB instances.

## Setup

### Option 1: Use Test Containers (Recommended)

```bash
# Start test containers
docker-compose -f tests/e2e/docker-compose.test.yml up -d

# Wait for services to be ready
sleep 30

# Run E2E tests
pytest tests/e2e/ -m e2e
```

### Option 2: Use Existing Instances

Set environment variables:

```bash
export E2E_HA_URL=http://localhost:8123
export E2E_HA_TOKEN=your_long_lived_token
export E2E_INFLUXDB_HOST=localhost
export E2E_INFLUXDB_PORT=8086
export E2E_INFLUXDB_DATABASE=test_find_my_history
export E2E_INFLUXDB_USERNAME=admin
export E2E_INFLUXDB_PASSWORD=password
```

## Running E2E Tests

```bash
# Run all E2E tests
pytest tests/e2e/ -m e2e -v

# Run specific test
pytest tests/e2e/test_full_workflow.py::TestFullWorkflow::test_ha_connection -v
```

## Test Requirements

- Home Assistant instance (running)
- InfluxDB instance (running)
- At least one device tracker configured in HA
- At least one zone configured in HA (optional, some tests will skip)

## Notes

- E2E tests are marked with `@pytest.mark.e2e`
- Tests will skip if environment variables are not set
- Tests may take longer to run (real network calls)
- Clean up test data after running tests
