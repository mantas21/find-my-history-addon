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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
_LOGGER = logging.getLogger(__name__)


def load_config() -> Dict:
    """Load configuration from environment variables (set by run.sh from options.json)."""
    # Parse devices from JSON string
    devices_str = os.environ.get("DEVICES", "[]")
    try:
        devices = json.loads(devices_str) if devices_str else []
    except json.JSONDecodeError:
        _LOGGER.warning(f"Could not parse DEVICES: {devices_str}")
        devices = []

    # Parse boolean
    focus_unknown_str = os.environ.get("FOCUS_UNKNOWN_LOCATIONS", "true")
    focus_unknown = focus_unknown_str.lower() in ("true", "1", "yes")

    # Get HA token - prefer SUPERVISOR_TOKEN (automatic when homeassistant_api: true)
    # Fall back to user-provided HA_TOKEN
    ha_token = os.environ.get("SUPERVISOR_TOKEN", "") or os.environ.get("HA_TOKEN", "")
    
    config = {
        "ha_url": os.environ.get("HA_URL", "http://supervisor/core"),
        "ha_token": ha_token,
        "check_interval": int(os.environ.get("CHECK_INTERVAL", "30")),
        "devices": devices,
        "influxdb_host": os.environ.get("INFLUXDB_HOST", "a0d7b954_influxdb"),
        "influxdb_port": int(os.environ.get("INFLUXDB_PORT", "8086")),
        "influxdb_database": os.environ.get("INFLUXDB_DATABASE", "find_my_history"),
        "influxdb_username": os.environ.get("INFLUXDB_USERNAME", "admin"),
        "influxdb_password": os.environ.get("INFLUXDB_PASSWORD", ""),
        "focus_unknown_locations": focus_unknown,
        "api_port": int(os.environ.get("API_PORT", "8090")),
    }

    # Validate required config - with homeassistant_api: true, SUPERVISOR_TOKEN is auto-provided
    if not config["ha_token"]:
        _LOGGER.error("No HA token available. Either set ha_token in config or enable homeassistant_api.")
        sys.exit(1)
    
    _LOGGER.info(f"Using {'Supervisor' if os.environ.get('SUPERVISOR_TOKEN') else 'user-provided'} token for HA API")

    if not config["devices"]:
        _LOGGER.warning("No devices configured. Add device_tracker entity IDs to 'devices' option.")

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
                _LOGGER.debug(f"Could not parse location from state: {state}")
                return None
        else:
            _LOGGER.debug(f"Entity {entity_state.get('entity_id')} has no location data")
            return None

    # Parse timestamp
    last_updated = entity_state.get("last_updated")
    timestamp = None
    if last_updated:
        try:
            timestamp = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            timestamp = datetime.utcnow()

    if timestamp is None:
        timestamp = datetime.utcnow()

    return {
        "latitude": float(latitude),
        "longitude": float(longitude),
        "accuracy": attributes.get("gps_accuracy"),
        "altitude": attributes.get("altitude"),
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
                in_zone=in_zone,
                zone_name=zone_name,
                timestamp=location_data["timestamp"]
            )

            if success:
                status = f"in zone '{zone_name}'" if in_zone else "unknown location"
                _LOGGER.info(
                    f"Stored location for {device_id} ({device_name}): "
                    f"({location_data['latitude']:.4f}, {location_data['longitude']:.4f}) - {status}"
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
    _LOGGER.info(f"Configuration loaded: {len(config['devices'])} devices configured")

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

    # Main polling loop
    check_interval = config["check_interval"] * 60  # Convert to seconds
    _LOGGER.info(f"Starting polling loop (interval: {config['check_interval']} minutes)")

    try:
        while True:
            # Refresh zones periodically (every 10 cycles)
            # This allows zones to be updated without restarting
            if not hasattr(main, "zone_refresh_counter"):
                main.zone_refresh_counter = 0

            main.zone_refresh_counter += 1
            if main.zone_refresh_counter >= 10:
                zones = ha_client.get_zones()
                zone_detector.update_zones(zones)
                main.zone_refresh_counter = 0

            # Poll devices
            if config["devices"]:
                poll_devices(
                    ha_client,
                    zone_detector,
                    influx_client,
                    config["devices"],
                    config["focus_unknown_locations"]
                )
            else:
                _LOGGER.warning("No devices configured. Waiting...")

            # Sleep until next poll
            _LOGGER.debug(f"Sleeping for {check_interval} seconds...")
            time.sleep(check_interval)

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
