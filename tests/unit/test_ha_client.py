"""Unit tests for ha_client module."""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from find_my_history.ha_client import HomeAssistantClient


class TestHomeAssistantClient:
    """Test HomeAssistantClient class."""

    def test_init(self):
        """Test client initialization."""
        client = HomeAssistantClient("http://test-ha:8123", "test-token")
        
        assert client.base_url == "http://test-ha:8123"
        assert client.token == "test-token"
        assert "Authorization" in client.headers
        assert client.headers["Authorization"] == "Bearer test-token"

    def test_init_strips_trailing_slash(self):
        """Test that base_url trailing slash is removed."""
        client = HomeAssistantClient("http://test-ha:8123/", "test-token")
        assert client.base_url == "http://test-ha:8123"

    @patch('find_my_history.ha_client.requests.request')
    def test_get_device_tracker_state_success(self, mock_request):
        """Test successful device tracker state retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "entity_id": "device_tracker.iphone",
            "state": "home",
            "attributes": {"latitude": 54.8985, "longitude": 23.9036}
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        client = HomeAssistantClient("http://test-ha:8123", "test-token")
        result = client.get_device_tracker_state("device_tracker.iphone")
        
        assert result is not None
        assert result["entity_id"] == "device_tracker.iphone"
        mock_request.assert_called_once()

    @patch('find_my_history.ha_client.requests.request')
    def test_get_device_tracker_state_error(self, mock_request):
        """Test device tracker state retrieval with error."""
        mock_request.side_effect = requests.exceptions.RequestException("Connection error")
        
        client = HomeAssistantClient("http://test-ha:8123", "test-token")
        result = client.get_device_tracker_state("device_tracker.iphone")
        
        assert result is None

    @patch('find_my_history.ha_client.requests.request')
    def test_get_all_device_trackers(self, mock_request):
        """Test getting all device trackers."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"entity_id": "device_tracker.iphone", "state": "home"},
            {"entity_id": "sensor.temperature", "state": "20"},
            {"entity_id": "device_tracker.ipad", "state": "not_home"},
        ]
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        client = HomeAssistantClient("http://test-ha:8123", "test-token")
        trackers = client.get_all_device_trackers()
        
        assert len(trackers) == 2
        assert all(t["entity_id"].startswith("device_tracker.") for t in trackers)

    @patch('find_my_history.ha_client.requests.request')
    def test_get_all_device_trackers_none_response(self, mock_request):
        """Test getting device trackers when API returns None."""
        mock_request.return_value = None
        mock_request.side_effect = requests.exceptions.RequestException("Error")
        
        client = HomeAssistantClient("http://test-ha:8123", "test-token")
        trackers = client.get_all_device_trackers()
        
        assert trackers == []

    @patch('find_my_history.ha_client.requests.request')
    def test_get_all_device_trackers_invalid_response(self, mock_request):
        """Test getting device trackers with invalid response type."""
        mock_response = Mock()
        mock_response.json.return_value = {"not": "a list"}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        client = HomeAssistantClient("http://test-ha:8123", "test-token")
        trackers = client.get_all_device_trackers()
        
        assert trackers == []

    @patch('find_my_history.ha_client.requests.request')
    def test_get_zones(self, mock_request):
        """Test getting zones from Home Assistant."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "entity_id": "zone.home",
                "attributes": {
                    "latitude": 54.8985,
                    "longitude": 23.9036,
                    "radius": 100,
                    "friendly_name": "Home",
                    "icon": "mdi:home"
                }
            },
            {
                "entity_id": "zone.work",
                "attributes": {
                    "latitude": 54.6872,
                    "longitude": 25.2797,
                    "radius": "50m",
                    "friendly_name": "Work"
                }
            },
            {
                "entity_id": "sensor.temp",
                "attributes": {}
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        client = HomeAssistantClient("http://test-ha:8123", "test-token")
        zones = client.get_zones()
        
        assert len(zones) == 2
        assert zones[0]["name"] == "Home"
        assert zones[0]["radius"] == 100.0
        assert zones[1]["radius"] == 50.0  # String "50m" converted to float

    @patch('find_my_history.ha_client.requests.request')
    def test_get_zones_no_zones(self, mock_request):
        """Test getting zones when none exist."""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        client = HomeAssistantClient("http://test-ha:8123", "test-token")
        zones = client.get_zones()
        
        assert zones == []

    @patch('find_my_history.ha_client.requests.request')
    def test_get_entity_state(self, mock_request):
        """Test getting any entity state."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "entity_id": "sensor.temperature",
            "state": "20"
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        client = HomeAssistantClient("http://test-ha:8123", "test-token")
        result = client.get_entity_state("sensor.temperature")
        
        assert result is not None
        assert result["entity_id"] == "sensor.temperature"

    @patch('find_my_history.ha_client.requests.request')
    def test_request_timeout(self, mock_request):
        """Test request timeout handling."""
        mock_request.side_effect = requests.exceptions.Timeout("Request timeout")
        
        client = HomeAssistantClient("http://test-ha:8123", "test-token")
        result = client.get_device_tracker_state("device_tracker.iphone")
        
        assert result is None
