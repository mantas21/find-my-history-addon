"""End-to-end tests for full workflow with real/test instances."""

import pytest
import os
import time
from datetime import datetime, timedelta

# These tests require real Home Assistant and InfluxDB instances
# Set environment variables to enable:
# E2E_HA_URL=http://localhost:8123
# E2E_HA_TOKEN=your_token
# E2E_INFLUXDB_HOST=localhost
# E2E_INFLUXDB_PORT=8086
# E2E_INFLUXDB_DATABASE=test_find_my_history
# E2E_INFLUXDB_USERNAME=admin
# E2E_INFLUXDB_PASSWORD=password


@pytest.mark.e2e
@pytest.mark.skipif(
    not os.getenv("E2E_HA_URL"),
    reason="E2E tests require E2E_HA_URL environment variable"
)
class TestFullWorkflow:
    """End-to-end tests with real services."""

    @pytest.fixture
    def ha_url(self):
        """Get Home Assistant URL from environment."""
        return os.getenv("E2E_HA_URL", "http://localhost:8123")

    @pytest.fixture
    def ha_token(self):
        """Get Home Assistant token from environment."""
        token = os.getenv("E2E_HA_TOKEN")
        if not token:
            pytest.skip("E2E_HA_TOKEN not set")
        return token

    @pytest.fixture
    def influxdb_config(self):
        """Get InfluxDB configuration from environment."""
        return {
            "host": os.getenv("E2E_INFLUXDB_HOST", "localhost"),
            "port": int(os.getenv("E2E_INFLUXDB_PORT", "8086")),
            "database": os.getenv("E2E_INFLUXDB_DATABASE", "test_find_my_history"),
            "username": os.getenv("E2E_INFLUXDB_USERNAME", "admin"),
            "password": os.getenv("E2E_INFLUXDB_PASSWORD", "password"),
        }

    def test_ha_connection(self, ha_url, ha_token):
        """Test connection to Home Assistant."""
        from find_my_history.ha_client import HomeAssistantClient
        
        client = HomeAssistantClient(ha_url, ha_token)
        trackers = client.get_all_device_trackers()
        
        assert isinstance(trackers, list)
        # Should not raise exception

    def test_influxdb_connection(self, influxdb_config):
        """Test connection to InfluxDB."""
        from find_my_history.influxdb_client import InfluxDBLocationClient
        
        client = InfluxDBLocationClient(
            host=influxdb_config["host"],
            port=influxdb_config["port"],
            database=influxdb_config["database"],
            username=influxdb_config["username"],
            password=influxdb_config["password"],
        )
        
        # Test write
        result = client.write_location(
            device_id="device_tracker.test_device",
            device_name="Test Device",
            latitude=54.8985,
            longitude=23.9036,
            timestamp=datetime.utcnow()
        )
        
        assert result is True
        
        # Test read
        locations = client.query_locations(device_id="device_tracker.test_device")
        assert isinstance(locations, list)
        
        client.close()

    def test_zone_detection_e2e(self, ha_url, ha_token):
        """Test zone detection with real Home Assistant zones."""
        from find_my_history.ha_client import HomeAssistantClient
        from find_my_history.zone_detector import ZoneDetector
        
        ha_client = HomeAssistantClient(ha_url, ha_token)
        zones = ha_client.get_zones()
        
        if not zones:
            pytest.skip("No zones configured in Home Assistant")
        
        detector = ZoneDetector(zones)
        
        # Test with first zone's coordinates
        zone = zones[0]
        lat = zone.get("latitude")
        lon = zone.get("longitude")
        
        if lat and lon:
            in_zone, zone_name = detector.check_zone(lat, lon)
            assert in_zone is True
            assert zone_name == zone.get("name")

    def test_full_location_workflow(self, ha_url, ha_token, influxdb_config):
        """Test full workflow: get location from HA, detect zone, store in InfluxDB."""
        from find_my_history.ha_client import HomeAssistantClient
        from find_my_history.zone_detector import ZoneDetector
        from find_my_history.influxdb_client import InfluxDBLocationClient
        
        # Get device tracker
        ha_client = HomeAssistantClient(ha_url, ha_token)
        trackers = ha_client.get_all_device_trackers()
        
        if not trackers:
            pytest.skip("No device trackers available")
        
        tracker = trackers[0]
        entity_id = tracker["entity_id"]
        attrs = tracker.get("attributes", {})
        
        lat = attrs.get("latitude")
        lon = attrs.get("longitude")
        
        if not lat or not lon:
            pytest.skip("Device tracker has no location data")
        
        # Detect zone
        zones = ha_client.get_zones()
        detector = ZoneDetector(zones)
        in_zone, zone_name = detector.check_zone(lat, lon)
        
        # Store in InfluxDB
        influx_client = InfluxDBLocationClient(
            host=influxdb_config["host"],
            port=influxdb_config["port"],
            database=influxdb_config["database"],
            username=influxdb_config["username"],
            password=influxdb_config["password"],
        )
        
        result = influx_client.write_location(
            device_id=entity_id,
            device_name=attrs.get("friendly_name", entity_id),
            latitude=lat,
            longitude=lon,
            accuracy=attrs.get("gps_accuracy"),
            battery_level=attrs.get("battery_level"),
            battery_state=attrs.get("battery_state"),
            in_zone=in_zone,
            zone_name=zone_name,
            timestamp=datetime.utcnow()
        )
        
        assert result is True
        
        # Verify we can read it back
        time.sleep(1)  # Give InfluxDB time to write
        locations = influx_client.query_locations(device_id=entity_id)
        
        assert len(locations) > 0
        assert locations[-1]["latitude"] == lat
        assert locations[-1]["longitude"] == lon
        
        influx_client.close()
