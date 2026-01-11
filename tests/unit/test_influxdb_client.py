"""Unit tests for influxdb_client module."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from find_my_history.influxdb_client import InfluxDBLocationClient


class TestInfluxDBLocationClient:
    """Test InfluxDBLocationClient class."""

    @patch('find_my_history.influxdb_client.InfluxDBClient')
    def test_init_influxdb_2x(self, mock_client_class):
        """Test initialization with InfluxDB 2.x."""
        mock_client = MagicMock()
        mock_write_api = MagicMock()
        mock_query_api = MagicMock()
        mock_client.write_api.return_value = mock_write_api
        mock_client.query_api.return_value = mock_query_api
        mock_client_class.return_value = mock_client
        
        client = InfluxDBLocationClient(
            host="test-influxdb",
            port=8086,
            database="test_db",
            username="test_user",
            password="test_pass"
        )
        
        assert client.host == "test-influxdb"
        assert client.port == 8086
        assert client.database == "test_db"
        assert client.version == 2
        mock_client_class.assert_called_once()

    @patch('find_my_history.influxdb_client.InfluxDBClient')
    def test_init_influxdb_1x_fallback(self, mock_client_class):
        """Test initialization falls back to InfluxDB 1.x on 2.x failure."""
        # First call (2.x) raises exception
        # Second call (1.x) succeeds
        mock_client = MagicMock()
        mock_write_api = MagicMock()
        mock_query_api = MagicMock()
        mock_client.write_api.return_value = mock_write_api
        mock_client.query_api.return_value = mock_query_api
        
        mock_client_class.side_effect = [
            Exception("2.x failed"),  # First call fails
            mock_client  # Second call succeeds
        ]
        
        client = InfluxDBLocationClient(
            host="test-influxdb",
            port=8086,
            database="test_db",
            username="test_user",
            password="test_pass"
        )
        
        assert client.version == 1
        assert mock_client_class.call_count == 2

    @patch('find_my_history.influxdb_client.InfluxDBClient')
    def test_write_location(self, mock_client_class):
        """Test writing location to InfluxDB."""
        mock_client = MagicMock()
        mock_write_api = MagicMock()
        mock_client.write_api.return_value = mock_write_api
        mock_client_class.return_value = mock_client
        
        client = InfluxDBLocationClient(
            host="test-influxdb",
            port=8086,
            database="test_db",
            username="test_user",
            password="test_pass"
        )
        
        result = client.write_location(
            device_id="device_tracker.iphone",
            device_name="iPhone",
            latitude=54.8985,
            longitude=23.9036,
            accuracy=10.0,
            battery_level=85,
            battery_state="not_charging",
            in_zone=True,
            zone_name="home"
        )
        
        assert result is True
        mock_write_api.write.assert_called_once()

    @patch('find_my_history.influxdb_client.InfluxDBClient')
    def test_write_location_error(self, mock_client_class):
        """Test writing location with error."""
        mock_client = MagicMock()
        mock_write_api = MagicMock()
        mock_write_api.write.side_effect = Exception("Write failed")
        mock_client.write_api.return_value = mock_write_api
        mock_client_class.return_value = mock_client
        
        client = InfluxDBLocationClient(
            host="test-influxdb",
            port=8086,
            database="test_db",
            username="test_user",
            password="test_pass"
        )
        
        result = client.write_location(
            device_id="device_tracker.iphone",
            device_name="iPhone",
            latitude=54.8985,
            longitude=23.9036
        )
        
        assert result is False

    @patch('find_my_history.influxdb_client.InfluxDBClient')
    def test_query_locations(self, mock_client_class):
        """Test querying locations from InfluxDB."""
        mock_client = MagicMock()
        mock_query_api = MagicMock()
        
        # Mock query results
        mock_record = MagicMock()
        mock_record.get_time.return_value = datetime(2025, 1, 27, 10, 0, 0)
        mock_record.get_field.return_value = "latitude"
        mock_record.get_value.return_value = 54.8985
        mock_record.values = {
            "device_id": "device_tracker.iphone",
            "device_name": "iPhone",
            "in_zone": "true",
            "zone_name": "home"
        }
        
        mock_table = MagicMock()
        mock_table.records = [mock_record]
        mock_query_api.query.return_value = [mock_table]
        
        mock_client.query_api.return_value = mock_query_api
        mock_client_class.return_value = mock_client
        
        client = InfluxDBLocationClient(
            host="test-influxdb",
            port=8086,
            database="test_db",
            username="test_user",
            password="test_pass"
        )
        
        locations = client.query_locations(device_id="device_tracker.iphone")
        
        assert isinstance(locations, list)
        mock_query_api.query.assert_called_once()

    @patch('find_my_history.influxdb_client.InfluxDBClient')
    def test_query_locations_error(self, mock_client_class):
        """Test querying locations with error."""
        mock_client = MagicMock()
        mock_query_api = MagicMock()
        mock_query_api.query.side_effect = Exception("Query failed")
        mock_client.query_api.return_value = mock_query_api
        mock_client_class.return_value = mock_client
        
        client = InfluxDBLocationClient(
            host="test-influxdb",
            port=8086,
            database="test_db",
            username="test_user",
            password="test_pass"
        )
        
        locations = client.query_locations()
        
        assert locations == []

    @patch('find_my_history.influxdb_client.InfluxDBClient')
    def test_get_unique_devices(self, mock_client_class):
        """Test getting unique device IDs."""
        mock_client = MagicMock()
        mock_query_api = MagicMock()
        
        mock_record = MagicMock()
        mock_record.get_value.return_value = "device_tracker.iphone"
        mock_table = MagicMock()
        mock_table.records = [mock_record]
        mock_query_api.query.return_value = [mock_table]
        
        mock_client.query_api.return_value = mock_query_api
        mock_client_class.return_value = mock_client
        
        client = InfluxDBLocationClient(
            host="test-influxdb",
            port=8086,
            database="test_db",
            username="test_user",
            password="test_pass"
        )
        
        devices = client.get_unique_devices()
        
        assert "device_tracker.iphone" in devices

    @patch('find_my_history.influxdb_client.InfluxDBClient')
    def test_close(self, mock_client_class):
        """Test closing client connection."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        client = InfluxDBLocationClient(
            host="test-influxdb",
            port=8086,
            database="test_db",
            username="test_user",
            password="test_pass"
        )
        
        client.close()
        mock_client.close.assert_called_once()

    @patch('find_my_history.influxdb_client.InfluxDBClient')
    def test_write_location_with_timestamp(self, mock_client_class):
        """Test writing location with custom timestamp."""
        mock_client = MagicMock()
        mock_write_api = MagicMock()
        mock_client.write_api.return_value = mock_write_api
        mock_client_class.return_value = mock_client
        
        client = InfluxDBLocationClient(
            host="test-influxdb",
            port=8086,
            database="test_db",
            username="test_user",
            password="test_pass"
        )
        
        custom_time = datetime(2025, 1, 27, 10, 0, 0)
        result = client.write_location(
            device_id="device_tracker.iphone",
            device_name="iPhone",
            latitude=54.8985,
            longitude=23.9036,
            timestamp=custom_time
        )
        
        assert result is True
        mock_write_api.write.assert_called_once()
