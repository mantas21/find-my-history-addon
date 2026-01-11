"""InfluxDB client for storing location data."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

_LOGGER = logging.getLogger(__name__)


class InfluxDBLocationClient:
    """Client for writing and reading location data from InfluxDB."""

    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str
    ):
        """
        Initialize InfluxDB client.

        Args:
            host: InfluxDB hostname
            port: InfluxDB port
            database: Database name
            username: InfluxDB username
            password: InfluxDB password
        """
        self.host = host
        self.port = port
        self.database = database
        self.url = f"http://{host}:{port}"
        
        # Try InfluxDB 2.x style first (with org), fallback to 1.x
        try:
            # For InfluxDB 2.x, use token format: username:password as token
            # and org can be empty or "-"
            self.client = InfluxDBClient(
                url=self.url,
                token=f"{username}:{password}" if username and password else "",
                org="-",
            )
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.query_api = self.client.query_api()
            # In InfluxDB 2.x, bucket = database name
            self.bucket = database
            self.version = 2
        except Exception as e:
            _LOGGER.warning(f"InfluxDB 2.x init failed, trying 1.x style: {e}")
            # Fallback: try with username/password directly
            try:
                self.client = InfluxDBClient(
                    url=self.url,
                    username=username,
                    password=password,
                )
                self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
                self.query_api = self.client.query_api()
                self.bucket = database
                self.version = 1
            except Exception as e2:
                _LOGGER.error(f"Failed to initialize InfluxDB client: {e2}")
                raise

    def write_location(
        self,
        device_id: str,
        device_name: str,
        latitude: float,
        longitude: float,
        accuracy: Optional[float] = None,
        altitude: Optional[float] = None,
        in_zone: bool = False,
        zone_name: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Write location data point to InfluxDB.

        Args:
            device_id: Entity ID (e.g., device_tracker.mantas_s_iphone)
            device_name: Friendly device name
            latitude: Device latitude
            longitude: Device longitude
            accuracy: Location accuracy in meters (optional)
            altitude: Device altitude in meters (optional)
            in_zone: Whether device is in a known zone
            zone_name: Zone name if in zone, None otherwise
            timestamp: Location timestamp (defaults to now)

        Returns:
            True if successful, False otherwise
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        try:
            point = (
                Point("device_location")
                .tag("device_id", device_id)
                .tag("device_name", device_name)
                .tag("in_zone", str(in_zone).lower())
                .tag("zone_name", zone_name or "unknown")
                .field("latitude", latitude)
                .field("longitude", longitude)
                .time(timestamp, WritePrecision.S)
            )

            if accuracy is not None:
                point = point.field("accuracy", float(accuracy))
            if altitude is not None:
                point = point.field("altitude", altitude)

            self.write_api.write(bucket=self.bucket, record=point)
            _LOGGER.debug(
                f"Wrote location for {device_id} at "
                f"({latitude}, {longitude})"
            )
            return True

        except Exception as e:
            _LOGGER.error(f"Failed to write location to InfluxDB: {e}")
            return False

    def query_locations(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """
        Query location history from InfluxDB.

        Args:
            device_id: Filter by device ID (optional)
            start_time: Start time for query (optional)
            end_time: End time for query (optional)
            limit: Maximum number of results

        Returns:
            List of location dictionaries
        """
        try:
            # Build Flux query for InfluxDB 2.x
            if not start_time:
                start_time = datetime.utcnow() - timedelta(days=30)
            if not end_time:
                end_time = datetime.utcnow()

            start_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

            query = f'''from(bucket: "{self.bucket}")
  |> range(start: {start_str}, stop: {end_str})
  |> filter(fn: (r) => r._measurement == "device_location")'''

            if device_id:
                query += f'\n  |> filter(fn: (r) => r.device_id == "{device_id}")'

            query += f'\n  |> limit(n: {limit})'

            # Execute query
            tables = self.query_api.query(query)

            # Parse results - InfluxDB returns data in pivoted format
            # Each record represents one field value at a timestamp
            # We need to group by timestamp and collect all fields
            location_map = {}

            for table in tables:
                for record in table.records:
                    time_key = record.get_time().isoformat()
                    
                    # Initialize location entry if not exists
                    if time_key not in location_map:
                        location_map[time_key] = {
                            "time": time_key,
                            "device_id": record.values.get("device_id", ""),
                            "device_name": record.values.get("device_name", ""),
                            "in_zone": record.values.get("in_zone", "false").lower() == "true",
                            "zone_name": record.values.get("zone_name", "unknown"),
                        }

                    # Add field value (latitude, longitude, accuracy, altitude)
                    field = record.get_field()
                    value = record.get_value()
                    if isinstance(value, (int, float)):
                        location_map[time_key][field] = float(value)

            # Convert to list, filter valid locations, and sort by time
            locations = [
                loc for loc in location_map.values()
                if "latitude" in loc and "longitude" in loc
            ]
            locations.sort(key=lambda x: x["time"])

            return locations

        except Exception as e:
            _LOGGER.error(f"Failed to query locations from InfluxDB: {e}", exc_info=True)
            return []

    def get_unique_devices(self) -> List[str]:
        """
        Get list of unique device IDs from InfluxDB.

        Returns:
            List of device entity IDs that have location data
        """
        try:
            # Query for unique device_id tag values
            query = f'''import "influxdata/influxdb/schema"
schema.tagValues(bucket: "{self.bucket}", tag: "device_id")'''

            tables = self.query_api.query(query)
            
            devices = []
            for table in tables:
                for record in table.records:
                    value = record.get_value()
                    if value:
                        devices.append(value)
            
            return devices

        except Exception as e:
            _LOGGER.warning(f"Failed to get unique devices from InfluxDB: {e}")
            return []

    def close(self):
        """Close InfluxDB client connections."""
        if self.client:
            self.client.close()
