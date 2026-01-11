"""HTTP API server for Lovelace card backend."""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from aiohttp import web
import aiohttp_cors

from find_my_history.ha_client import HomeAssistantClient
from find_my_history.influxdb_client import InfluxDBLocationClient
from find_my_history.device_prefs import get_device_prefs
from find_my_history.zone_detector import ZoneDetector

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
        
        # Initialize zone detector
        zones = ha_client.get_zones()
        self.zone_detector = ZoneDetector(zones)
        
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
        self.app.router.add_post("/api/devices/toggle", self.toggle_device)
        self.app.router.add_post("/api/devices/update", self.update_device_location)
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
        """Get list of all device_tracker entities with tracking status."""
        try:
            devices = []
            prefs = get_device_prefs()
            
            # Try to get device trackers from HA
            trackers = self.ha_client.get_all_device_trackers()
            
            if trackers:
                for tracker in trackers:
                    entity_id = tracker.get("entity_id", "")
                    if entity_id.startswith("device_tracker."):
                        devices.append({
                            "entity_id": entity_id,
                            "name": tracker.get("attributes", {}).get("friendly_name", entity_id),
                            "state": tracker.get("state"),
                            "is_tracked": prefs.is_tracked(entity_id),
                            "interval_minutes": prefs.get_interval(entity_id, 5),
                        })
            
            # If no devices from HA, try to get unique devices from InfluxDB
            if not devices:
                try:
                    influx_devices = self.influx_client.get_unique_devices()
                    for device_id in influx_devices:
                        devices.append({
                            "entity_id": device_id,
                            "name": device_id.replace("device_tracker.", "").replace("_", " ").title(),
                            "state": "unknown",
                            "is_tracked": prefs.is_tracked(device_id),
                            "interval_minutes": prefs.get_interval(device_id, 5),
                        })
                except Exception as e:
                    _LOGGER.warning(f"Could not get devices from InfluxDB: {e}")

            # Sort: tracked devices first, then alphabetically
            devices.sort(key=lambda d: (not d["is_tracked"], d["name"].lower()))

            return web.json_response({"devices": devices})

        except Exception as e:
            _LOGGER.error(f"Error in get_devices: {e}", exc_info=True)
            return web.json_response(
                {"error": str(e)}, status=500
            )

    async def toggle_device(self, request: web.Request) -> web.Response:
        """Toggle device tracking status."""
        try:
            data = await request.json()
            entity_id = data.get("entity_id")
            interval_minutes = data.get("interval_minutes", 5)
            
            if not entity_id:
                return web.json_response(
                    {"error": "entity_id is required"}, status=400
                )
            
            prefs = get_device_prefs()
            is_now_tracked = prefs.toggle_device(entity_id, interval_minutes)
            
            _LOGGER.info(f"Device {entity_id} tracking toggled: {'ON' if is_now_tracked else 'OFF'}")
            
            return web.json_response({
                "entity_id": entity_id,
                "is_tracked": is_now_tracked,
                "message": f"Device tracking {'enabled' if is_now_tracked else 'disabled'}"
            })

        except json.JSONDecodeError:
            return web.json_response(
                {"error": "Invalid JSON body"}, status=400
            )
        except Exception as e:
            _LOGGER.error(f"Error in toggle_device: {e}", exc_info=True)
            return web.json_response(
                {"error": str(e)}, status=500
            )

    async def update_device_location(self, request: web.Request) -> web.Response:
        """Force refresh location for a specific device."""
        try:
            data = await request.json()
            device_id = data.get("device_id")
            
            if not device_id:
                return web.json_response(
                    {"error": "device_id is required"}, status=400
                )
            
            # Get current state from HA
            entity_state = self.ha_client.get_device_tracker_state(device_id)
            if not entity_state:
                return web.json_response(
                    {"error": "Device not found"}, status=404
                )
            
            # Extract location data
            attributes = entity_state.get("attributes", {})
            latitude = attributes.get("latitude")
            longitude = attributes.get("longitude")
            
            if latitude is None or longitude is None:
                return web.json_response(
                    {"error": "No location data available"}, status=400
                )
            
            # Get device info
            device_name = attributes.get("friendly_name", device_id)
            accuracy = attributes.get("gps_accuracy")
            altitude = attributes.get("altitude")
            battery_level = attributes.get("battery_level")
            battery_state = attributes.get("battery_state")
            
            # Check zone
            in_zone, zone_name = self.zone_detector.check_zone(
                float(latitude), float(longitude)
            )
            
            # Current timestamp
            timestamp = datetime.utcnow()
            
            # Store in InfluxDB
            success = self.influx_client.write_location(
                device_id=device_id,
                device_name=device_name,
                latitude=float(latitude),
                longitude=float(longitude),
                accuracy=accuracy,
                altitude=altitude,
                battery_level=battery_level,
                battery_state=battery_state,
                in_zone=in_zone,
                zone_name=zone_name,
                timestamp=timestamp
            )
            
            if success:
                _LOGGER.info(f"Manually updated location for {device_id}")
                return web.json_response({
                    "success": True,
                    "location": {
                        "latitude": float(latitude),
                        "longitude": float(longitude),
                        "battery_level": battery_level,
                        "battery_state": battery_state,
                        "zone_name": zone_name,
                        "in_zone": in_zone,
                        "timestamp": timestamp.isoformat()
                    }
                })
            else:
                return web.json_response(
                    {"error": "Failed to store location"}, status=500
                )
                
        except json.JSONDecodeError:
            return web.json_response(
                {"error": "Invalid JSON body"}, status=400
            )
        except Exception as e:
            _LOGGER.error(f"Error in update_device_location: {e}", exc_info=True)
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
