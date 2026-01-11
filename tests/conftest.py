"""Pytest configuration and shared fixtures."""

import pytest
import json
import os
from typing import Dict, List
from unittest.mock import Mock, MagicMock
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "find_my_history_addon"))


@pytest.fixture
def sample_zones() -> List[Dict]:
    """Sample Home Assistant zones for testing."""
    return [
        {
            "name": "home",
            "latitude": 54.8985,
            "longitude": 23.9036,
            "radius": 100,
        },
        {
            "name": "work",
            "latitude": 54.6872,
            "longitude": 25.2797,
            "radius": 50,
        },
        {
            "name": "gym",
            "latitude": 54.9000,
            "longitude": 23.9000,
            "radius": 25,
        },
    ]


@pytest.fixture
def sample_device_trackers() -> List[Dict]:
    """Sample device tracker states for testing."""
    return [
        {
            "entity_id": "device_tracker.iphone",
            "state": "home",
            "attributes": {
                "latitude": 54.8985,
                "longitude": 23.9036,
                "gps_accuracy": 10,
                "battery_level": 85,
                "battery_state": "not_charging",
                "friendly_name": "iPhone",
            },
        },
        {
            "entity_id": "device_tracker.ipad",
            "state": "not_home",
            "attributes": {
                "latitude": 54.7000,
                "longitude": 25.2000,
                "gps_accuracy": 15,
                "battery_level": 45,
                "battery_state": "charging",
                "friendly_name": "iPad",
            },
        },
    ]


@pytest.fixture
def sample_location_data() -> Dict:
    """Sample location data for testing."""
    return {
        "device_id": "device_tracker.iphone",
        "device_name": "iPhone",
        "latitude": 54.8985,
        "longitude": 23.9036,
        "accuracy": 10.0,
        "altitude": 100.0,
        "battery_level": 85,
        "battery_state": "not_charging",
    }


@pytest.fixture
def mock_ha_client():
    """Mock Home Assistant client."""
    client = Mock()
    client.base_url = "http://test-ha:8123"
    client.token = "test-token"
    return client


@pytest.fixture
def mock_influxdb_client():
    """Mock InfluxDB client."""
    client = Mock()
    client.host = "test-influxdb"
    client.port = 8086
    client.database = "test_db"
    return client


@pytest.fixture
def mock_api_response():
    """Mock API response helper."""
    def _create_response(data, status=200):
        response = Mock()
        response.status = status
        response.json.return_value = data
        response.text = json.dumps(data)
        return response
    return _create_response


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("HA_URL", "http://test-ha:8123")
    monkeypatch.setenv("HA_TOKEN", "test-token")
    monkeypatch.setenv("INFLUXDB_HOST", "test-influxdb")
    monkeypatch.setenv("INFLUXDB_PORT", "8086")
    monkeypatch.setenv("INFLUXDB_DATABASE", "test_db")
    monkeypatch.setenv("INFLUXDB_USERNAME", "test_user")
    monkeypatch.setenv("INFLUXDB_PASSWORD", "test_pass")
    monkeypatch.setenv("DEFAULT_INTERVAL", "5")
    monkeypatch.setenv("TRACKED_DEVICES", "[]")
