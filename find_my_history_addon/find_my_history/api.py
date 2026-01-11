"""HTTP API server for Lovelace card backend."""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from aiohttp import web
import aiohttp_cors

from find_my_history.ha_client import HomeAssistantClient
from find_my_history.influxdb_client import InfluxDBLocationClient

_LOGGER = logging.getLogger(__name__)

# Path to static files
STATIC_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'www')


class LocationHistoryAPI:
    """HTTP API server for location history data."""

    def __init__(
        self,
        ha_client: HomeAssistantClient,
        influx_client: InfluxDBLocationClient,
        port: int = 8080
    ):
        """
        Initialize API server.

        Args:
            ha_client: Home Assistant API client
            influx_client: InfluxDB client
            port: Port to listen on
        """
        self.ha_client = ha_client
        self.influx_client = influx_client
        self.port = port
        self.app = web.Application()
        self._setup_routes()

    def _setup_routes(self):
        """Set up API routes."""
        # Enable CORS for Lovelace card
        cors = aiohttp_cors.setup(
            self.app,
            defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods="*"
                )
            }
        )

        # API Routes
        self.app.router.add_get("/api/locations", self.get_locations)
        self.app.router.add_get("/api/zones", self.get_zones)
        self.app.router.add_get("/api/devices", self.get_devices)
        self.app.router.add_get("/api/stats", self.get_stats)
        self.app.router.add_get("/health", self.health_check)
        
        # Static files and index page
        self.app.router.add_get("/", self.serve_index)
        self.app.router.add_static("/static", STATIC_PATH)

        # Enable CORS for all routes
        for route in list(self.app.router.routes()):
            try:
                cors.add(route)
            except ValueError:
                pass  # Static routes don't need CORS

    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint."""
        return web.json_response({"status": "ok"})

    async def serve_index(self, request: web.Request) -> web.Response:
        """Serve the main HTML page."""
        index_path = os.path.join(STATIC_PATH, 'index.html')
        if os.path.exists(index_path):
            return web.FileResponse(index_path)
        return web.Response(
            text="<html><body><h1>Find My Location History</h1><p>API is running. Access /api/health for status.</p></body></html>",
            content_type='text/html'
        )

    async def get_locations(self, request: web.Request) -> web.Response:
        """
        Get location history.

        Query params:
            device_id: Device entity ID (optional)
            start: Start timestamp (ISO format, optional)
            end: End timestamp (ISO format, optional)
            limit: Maximum results (default: 1000)
        """
        try:
            device_id = request.query.get("device_id")
            start_str = request.query.get("start")
            end_str = request.query.get("end")
            limit = int(request.query.get("limit", 1000))

            start_time = None
            end_time = None

            if start_str:
                try:
                    start_time = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                except ValueError:
                    return web.json_response(
                        {"error": "Invalid start timestamp format"}, status=400
                    )

            if end_str:
                try:
                    end_time = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
                except ValueError:
                    return web.json_response(
                        {"error": "Invalid end timestamp format"}, status=400
                    )

            locations = self.influx_client.query_locations(
                device_id=device_id,
                start_time=start_time,
                end_time=end_time,
                limit=limit
            )

            return web.json_response({"locations": locations})

        except Exception as e:
            _LOGGER.error(f"Error in get_locations: {e}", exc_info=True)
            return web.json_response(
                {"error": str(e)}, status=500
            )

    async def get_zones(self, request: web.Request) -> web.Response:
        """Get all Home Assistant zones."""
        try:
            zones = self.ha_client.get_zones()
            return web.json_response({"zones": zones})
        except Exception as e:
            _LOGGER.error(f"Error in get_zones: {e}", exc_info=True)
            return web.json_response(
                {"error": str(e)}, status=500
            )

    async def get_devices(self, request: web.Request) -> web.Response:
        """Get list of tracked devices."""
        try:
            # Get all device trackers
            trackers = self.ha_client.get_all_device_trackers()
            
            devices = []
            for tracker in trackers:
                entity_id = tracker.get("entity_id", "")
                if entity_id.startswith("device_tracker."):
                    devices.append({
                        "entity_id": entity_id,
                        "name": tracker.get("attributes", {}).get("friendly_name", entity_id),
                        "state": tracker.get("state"),
                    })

            return web.json_response({"devices": devices})

        except Exception as e:
            _LOGGER.error(f"Error in get_devices: {e}", exc_info=True)
            return web.json_response(
                {"error": str(e)}, status=500
            )

    async def get_stats(
        self, request: web.Request
    ) -> web.Response:
        """
        Get statistics for a device.

        Query params:
            device_id: Device entity ID (required)
            start: Start timestamp (ISO format, optional)
            end: End timestamp (ISO format, optional)
        """
        try:
            device_id = request.query.get("device_id")
            if not device_id:
                return web.json_response(
                    {"error": "device_id parameter required"}, status=400
                )

            start_str = request.query.get("start")
            end_str = request.query.get("end")

            start_time = None
            end_time = None

            if start_str:
                try:
                    start_time = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                except ValueError:
                    return web.json_response(
                        {"error": "Invalid start timestamp format"}, status=400
                    )

            if end_str:
                try:
                    end_time = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
                except ValueError:
                    return web.json_response(
                        {"error": "Invalid end timestamp format"}, status=400
                    )

            # Default to last 24 hours if not specified
            if not end_time:
                end_time = datetime.utcnow()
            if not start_time:
                start_time = end_time - timedelta(days=1)

            # Query locations
            locations = self.influx_client.query_locations(
                device_id=device_id,
                start_time=start_time,
                end_time=end_time,
                limit=10000
            )

            # Calculate statistics
            total_points = len(locations)
            in_zone_count = sum(1 for loc in locations if loc.get("in_zone", False))
            unknown_count = total_points - in_zone_count

            # Calculate time spans
            if locations:
                try:
                    first_time_str = locations[0]["time"].replace("Z", "+00:00")
                    last_time_str = locations[-1]["time"].replace("Z", "+00:00")
                    first_time = datetime.fromisoformat(first_time_str)
                    last_time = datetime.fromisoformat(last_time_str)
                    total_duration = (last_time - first_time).total_seconds()
                except (ValueError, KeyError) as e:
                    _LOGGER.warning(f"Error parsing timestamps: {e}")
                    total_duration = 0
            else:
                total_duration = 0

            stats = {
                "device_id": device_id,
                "period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                },
                "total_locations": total_points,
                "in_zone": {
                    "count": in_zone_count,
                    "percentage": (in_zone_count / total_points * 100) if total_points > 0 else 0,
                },
                "unknown": {
                    "count": unknown_count,
                    "percentage": (unknown_count / total_points * 100) if total_points > 0 else 0,
                },
                "duration_seconds": total_duration,
            }

            return web.json_response(stats)

        except Exception as e:
            _LOGGER.error(f"Error in get_stats: {e}", exc_info=True)
            return web.json_response(
                {"error": str(e)}, status=500
            )

    async def run(self):
        """Run the API server."""
        _LOGGER.info(f"Starting API server on port {self.port}")
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", self.port)
        await site.start()
        _LOGGER.info(f"API server started on http://0.0.0.0:{self.port}")
