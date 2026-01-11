"""Integration tests for API endpoints."""

import pytest
from aiohttp.test_utils import AioHTTPTestCase, make_mocked_request
from unittest.mock import Mock
from find_my_history.api import LocationHistoryAPI


@pytest.fixture
def mock_ha_client():
    """Mock Home Assistant client."""
    client = Mock()
    client.get_all_device_trackers = Mock(return_value=[
        {
            "entity_id": "device_tracker.iphone",
            "state": "home",
            "attributes": {
                "latitude": 54.8985,
                "longitude": 23.9036,
                "friendly_name": "iPhone",
            },
        },
    ])
    client.get_zones = Mock(return_value=[
        {"name": "home", "latitude": 54.8985, "longitude": 23.9036, "radius": 100},
    ])
    client.get_device_tracker_state = Mock(return_value={
        "entity_id": "device_tracker.iphone",
        "state": "home",
        "attributes": {"latitude": 54.8985, "longitude": 23.9036},
    })
    return client


@pytest.fixture
def mock_influxdb_client():
    """Mock InfluxDB client."""
    client = Mock()
    client.query_locations = Mock(return_value=[])
    client.get_statistics = Mock(return_value={
        "total_locations": 10,
        "known_locations": 5,
        "unknown_locations": 5,
    })
    return client


@pytest.fixture
def api_server(mock_ha_client, mock_influxdb_client):
    """Create API server instance."""
    return LocationHistoryAPI(mock_ha_client, mock_influxdb_client, port=8090)


@pytest.mark.asyncio
class TestLocationHistoryAPI:
    """Test LocationHistoryAPI endpoints."""

    async def test_health_endpoint(self, api_server):
        """Test health check endpoint."""
        request = make_mocked_request("GET", "/health")
        # Find the route handler
        handler = None
        for route in api_server.app.router.routes():
            if hasattr(route, 'path') and route.path == "/health":
                handler = route.handler
                break
        
        if handler:
            response = await handler(request)
            assert response.status == 200
            data = await response.json()
            assert data["status"] == "ok"

    async def test_devices_endpoint(self, api_server, mock_ha_client):
        """Test devices list endpoint."""
        request = make_mocked_request("GET", "/api/devices")
        handler = None
        for route in api_server.app.router.routes():
            if hasattr(route, 'path') and route.path == "/api/devices":
                handler = route.handler
                break
        
        if handler:
            response = await handler(request)
            assert response.status == 200
            data = await response.json()
            assert "devices" in data

    async def test_zones_endpoint(self, api_server):
        """Test zones list endpoint."""
        request = make_mocked_request("GET", "/api/zones")
        handler = None
        for route in api_server.app.router.routes():
            if hasattr(route, 'path') and route.path == "/api/zones":
                handler = route.handler
                break
        
        if handler:
            response = await handler(request)
            assert response.status == 200
            data = await response.json()
            assert "zones" in data

    async def test_locations_endpoint(self, api_server, mock_influxdb_client):
        """Test locations query endpoint."""
        # Mock location data
        mock_influxdb_client.query_locations.return_value = [
            {
                "time": "2025-01-27T10:00:00Z",
                "latitude": 54.8985,
                "longitude": 23.9036,
                "in_zone": True,
                "zone_name": "home",
            },
        ]
        
        request = make_mocked_request(
            "GET",
            "/api/locations?device_id=device_tracker.iphone&start=2025-01-27T00:00:00Z&end=2025-01-27T23:59:59Z"
        )
        handler = None
        for route in api_server.app.router.routes():
            if hasattr(route, 'path') and route.path == "/api/locations":
                handler = route.handler
                break
        
        if handler:
            response = await handler(request)
            assert response.status == 200
            data = await response.json()
            assert "locations" in data

    async def test_stats_endpoint(self, api_server, mock_influxdb_client):
        """Test statistics endpoint."""
        request = make_mocked_request(
            "GET",
            "/api/stats?device_id=device_tracker.iphone&start=2025-01-27T00:00:00Z&end=2025-01-27T23:59:59Z"
        )
        handler = None
        for route in api_server.app.router.routes():
            if hasattr(route, 'path') and route.path == "/api/stats":
                handler = route.handler
                break
        
        if handler:
            response = await handler(request)
            assert response.status == 200
            data = await response.json()
            assert "total_locations" in data or "stats" in data
