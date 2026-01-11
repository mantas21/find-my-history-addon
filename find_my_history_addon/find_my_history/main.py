"""Main polling service for Find My Location History add-on."""

import os
import sys
import time
import logging
import json
import threading
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from find_my_history.ha_client import HomeAssistantClient
from find_my_history.zone_detector import ZoneDetector
from find_my_history.influxdb_client import InfluxDBLocationClient
from find_my_history.api import LocationHistoryAPI
from find_my_history.device_prefs import get_device_prefs
from find_my_history.log_utils import format_coordinates, setup_secure_logging

# Configure secure logging
setup_secure_logging(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


def load_config() -> Dict:
    """Load configuration from environment variables (set by run.sh from options.json)."""
    # Parse tracked_devices from JSON string (new format with per-device intervals)
    tracked_devices_str = os.environ.get("TRACKED_DEVICES", "[]")
    try:
        tracked_devices = json.loads(tracked_devices_str) if tracked_devices_str else []
    except json.JSONDecodeError:
        _LOGGER.warning(f"Could not parse TRACKED_DEVICES: {tracked_devices_str}")
        tracked_devices = []

    # Also support old DEVICES format for backward compatibility
    if not tracked_devices:
        devices_str = os.environ.get("DEVICES", "[]")
        try:
            old_devices = json.loads(devices_str) if devices_str else []
            # Convert old format (list of strings) to new format
            default_interval = int(os.environ.get("DEFAULT_INTERVAL", "5"))
            tracked_devices = [
                {"entity_id": d, "interval_minutes": default_interval, "enabled": True}
                for d in old_devices if isinstance(d, str)
            ]
        except json.JSONDecodeError:
            pass

    # Filter enabled devices and remove example entries
    tracked_devices = [
        d for d in tracked_devices 
        if d.get("enabled", True) and d.get("entity_id") and "example" not in d.get("entity_id", "")
    ]

    # Parse boolean
    focus_unknown_str = os.environ.get("FOCUS_UNKNOWN_LOCATIONS", "true")
    focus_unknown = focus_unknown_str.lower() in ("true", "1", "yes")

    # Get HA token - prefer SUPERVISOR_TOKEN (automatic when homeassistant_api: true)
    ha_token = os.environ.get("SUPERVISOR_TOKEN", "") or os.environ.get("HA_TOKEN", "")
    
    config = {
        "ha_url": os.environ.get("HA_URL", "http://supervisor/core"),
        "ha_token": ha_token,
        "default_interval": int(os.environ.get("DEFAULT_INTERVAL", "5")),
        "tracked_devices": tracked_devices,
        "influxdb_host": os.environ.get("INFLUXDB_HOST", "a0d7b954-influxdb"),
        "influxdb_port": int(os.environ.get("INFLUXDB_PORT", "8086")),
        "influxdb_database": os.environ.get("INFLUXDB_DATABASE", "find_my_history"),
        "influxdb_username": os.environ.get("INFLUXDB_USERNAME", "admin"),
        "influxdb_password": os.environ.get("INFLUXDB_PASSWORD", ""),
        "focus_unknown_locations": focus_unknown,
        "api_port": int(os.environ.get("API_PORT", "8090")),
    }

    # Validate required config
    if not config["ha_token"]:
        _LOGGER.error("No HA token available. Either set ha_token in config or enable homeassistant_api.")
        sys.exit(1)
    
    _LOGGER.info(f"Using {'Supervisor' if os.environ.get('SUPERVISOR_TOKEN') else 'user-provided'} token for HA API")

    if not config["tracked_devices"]:
        _LOGGER.warning("No devices configured. Add devices in the add-on configuration.")

    return config


def extract_location_data(entity_state: Dict) -> Optional[Dict]:
    """
    Extract location data from device_tracker entity state.

    Args:
        entity_state: Entity state dictionary from HA API

    Returns:
        Dict with latitude, longitude, accuracy, altitude, timestamp
        or None if invalid
    """
    if not entity_state:
        return None

    state = entity_state.get("state")
    attributes = entity_state.get("attributes", {})

    # Check if state is a location (latitude, longitude format)
    latitude = attributes.get("latitude")
    longitude = attributes.get("longitude")

    if latitude is None or longitude is None:
        # Try parsing state as "latitude, longitude" string
        if isinstance(state, str) and "," in state:
            try:
                parts = state.split(",")
                latitude = float(parts[0].strip())
                longitude = float(parts[1].strip())
            except (ValueError, IndexError):
                # Don't log the state value as it may contain sensitive location data
                _LOGGER.debug(f"Could not parse location from entity state")
                return None
        else:
            entity_id = entity_state.get('entity_id', 'unknown')
            _LOGGER.debug(f"Entity {entity_id} has no location data")
            return None

    # Use current time for poll timestamp (not entity's last_updated)
    # This ensures each poll creates a new data point even if device hasn't moved
    timestamp = datetime.utcnow()

    return {
        "latitude": float(latitude),
        "longitude": float(longitude),
        "accuracy": attributes.get("gps_accuracy"),
        "altitude": attributes.get("altitude"),
        "battery_level": attributes.get("battery_level"),
        "battery_state": attributes.get("battery_state"),  # "charging" or "not_charging"
        "timestamp": timestamp,
    }


def poll_devices(
    ha_client: HomeAssistantClient,
    zone_detector: ZoneDetector,
    influx_client: InfluxDBLocationClient,
    device_ids: List[str],
    focus_unknown: bool
):
    """
    Poll all configured devices and store their locations.

    Args:
        ha_client: Home Assistant API client
        zone_detector: Zone detector instance
        influx_client: InfluxDB client
        device_ids: List of device_tracker entity IDs to poll
        focus_unknown: Whether to focus on unknown locations
    """
    _LOGGER.info(f"Polling {len(device_ids)} devices...")

    for device_id in device_ids:
        try:
            # Get device state from HA
            entity_state = ha_client.get_device_tracker_state(device_id)
            if not entity_state:
                _LOGGER.warning(f"Could not get state for {device_id}")
                continue

            # Extract location data
            location_data = extract_location_data(entity_state)
            if not location_data:
                _LOGGER.debug(f"No location data for {device_id}")
                continue

            # Check if in zone
            in_zone, zone_name = zone_detector.check_zone(
                location_data["latitude"],
                location_data["longitude"]
            )

            # Get device friendly name
            device_name = entity_state.get("attributes", {}).get("friendly_name", device_id)

            # Store in InfluxDB
            success = influx_client.write_location(
                device_id=device_id,
                device_name=device_name,
                latitude=location_data["latitude"],
                longitude=location_data["longitude"],
                accuracy=location_data.get("accuracy"),
                altitude=location_data.get("altitude"),
                battery_level=location_data.get("battery_level"),
                battery_state=location_data.get("battery_state"),
                in_zone=in_zone,
                zone_name=zone_name,
                timestamp=location_data["timestamp"]
            )

            if success:
                status = f"in zone '{zone_name}'" if in_zone else "unknown location"
                coords = format_coordinates(
                    location_data['latitude'],
                    location_data['longitude'],
                    precision=4
                )
                _LOGGER.info(
                    f"Stored location for {device_id} ({device_name}): "
                    f"{coords} - {status}"
                )
            else:
                _LOGGER.error(f"Failed to store location for {device_id}")

        except Exception as e:
            _LOGGER.error(f"Error processing device {device_id}: {e}", exc_info=True)


def run_api_server(api: LocationHistoryAPI):
    """Run API server in background thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(api.run())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


def main():
    """Main entry point."""
    _LOGGER.info("Starting Find My Location History add-on...")

    # Load configuration
    config = load_config()
    
    # Initialize device preferences (persistent storage)
    prefs = get_device_prefs()
    
    # Sync devices from add-on config to preferences
    # Config is the source of truth for intervals, UI manages which devices are tracked
    config_devices = config.get("tracked_devices", [])
    if config_devices:
        existing_tracked = prefs.get_tracked_devices()
        
        for dev in config_devices:
            entity_id = dev.get("entity_id")
            interval = dev.get("interval_minutes", 5)
            enabled = dev.get("enabled", True)
            
            if not entity_id or "example" in entity_id:
                continue
                
            if enabled:
                if entity_id not in existing_tracked:
                    # Add new device from config
                    prefs.add_device(entity_id, interval)
                    _LOGGER.info(f"Added device from config: {entity_id} (interval: {interval}m)")
                else:
                    # Update interval from config
                    prefs.set_interval(entity_id, interval)
                    _LOGGER.debug(f"Updated interval from config: {entity_id} -> {interval}m")
    
    # Log current tracked devices
    tracked = prefs.get_tracked_with_intervals()
    _LOGGER.info(f"Device preferences loaded: {len(tracked)} devices tracked")
    for dev in tracked:
        _LOGGER.info(f"  - {dev['entity_id']}: every {dev.get('interval_minutes', 5)} minutes")

    # Initialize clients
    ha_client = HomeAssistantClient(config["ha_url"], config["ha_token"])
    influx_client = InfluxDBLocationClient(
        host=config["influxdb_host"],
        port=config["influxdb_port"],
        database=config["influxdb_database"],
        username=config["influxdb_username"],
        password=config["influxdb_password"]
    )

    # Get initial zones
    zones = ha_client.get_zones()
    zone_detector = ZoneDetector(zones)
    _LOGGER.info(f"Loaded {len(zones)} zones")

    # Start API server in background thread
    api_port = config["api_port"]
    api = LocationHistoryAPI(ha_client, influx_client, port=api_port)
    api_thread = threading.Thread(target=run_api_server, args=(api,), daemon=True)
    api_thread.start()
    _LOGGER.info(f"API server started on port {api_port}")

    # Track last poll time for each device
    last_poll_times: Dict[str, float] = {}
    zone_refresh_counter = 0
    
    # Base check interval (1 minute) - check if any device needs updating
    base_interval = 60
    _LOGGER.info("Starting polling loop with dynamic device tracking")

    try:
        while True:
            current_time = time.time()
            
            # Refresh zones periodically (every 10 base cycles = 10 minutes)
            zone_refresh_counter += 1
            if zone_refresh_counter >= 10:
                zones = ha_client.get_zones()
                zone_detector.update_zones(zones)
                zone_refresh_counter = 0

            # Get current tracked devices (re-read from prefs for hot reload)
            tracked_devices = prefs.get_tracked_with_intervals()
            
            # Check each device if it needs to be polled
            devices_to_poll = []
            for dev in tracked_devices:
                entity_id = dev["entity_id"]
                interval_seconds = dev.get("interval_minutes", 5) * 60
                last_poll = last_poll_times.get(entity_id, 0)
                
                if current_time - last_poll >= interval_seconds:
                    devices_to_poll.append(entity_id)
                    last_poll_times[entity_id] = current_time

            # Poll devices that need updating
            if devices_to_poll:
                poll_devices(
                    ha_client,
                    zone_detector,
                    influx_client,
                    devices_to_poll,
                    config["focus_unknown_locations"]
                )
            
            if not tracked_devices:
                _LOGGER.debug("No devices tracked. Use the web UI to add devices.")

            # Sleep for base interval
            time.sleep(base_interval)

    except KeyboardInterrupt:
        _LOGGER.info("Received interrupt signal, shutting down...")
    except Exception as e:
        _LOGGER.error(f"Fatal error in main loop: {e}", exc_info=True)
        sys.exit(1)
    finally:
        influx_client.close()
        _LOGGER.info("Add-on stopped")


if __name__ == "__main__":
    main()
