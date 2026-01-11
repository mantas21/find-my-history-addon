"""Zone detection logic for determining if device is in a known zone."""

import logging
import math
from typing import Dict, List, Optional, Tuple

from find_my_history.log_utils import format_coordinates

_LOGGER = logging.getLogger(__name__)


class ZoneDetector:
    """Detects if a location is within Home Assistant zones."""

    def __init__(self, zones: List[Dict]):
        """
        Initialize zone detector.

        Args:
            zones: List of zone dictionaries from HA zone registry
        """
        self.zones = zones
        _LOGGER.info(f"Initialized with {len(zones)} zones")
        for zone in zones:
            name = zone.get("name", "unknown")
            lat = zone.get("latitude")
            lon = zone.get("longitude")
            radius = zone.get("radius", 100)
            coords = format_coordinates(lat, lon, precision=5)
            _LOGGER.info(f"  Zone: {name} @ {coords} radius={radius}m")

    def _calculate_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.

        Returns:
            Distance in meters
        """
        # Earth radius in meters
        R = 6371000

        # Convert to radians
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        # Haversine formula
        a = (
            math.sin(delta_phi / 2) ** 2 +
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def check_zone(
        self, latitude: float, longitude: float
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if location is within any zone.

        Args:
            latitude: Device latitude
            longitude: Device longitude

        Returns:
            Tuple of (in_zone (bool), zone_name (str or None))
        """
        if not self.zones:
            _LOGGER.warning("No zones loaded for zone detection")
            return False, None

        closest_zone = None
        closest_distance = float('inf')
        
        for zone in self.zones:
            zone_lat = zone.get("latitude")
            zone_lon = zone.get("longitude")
            zone_radius_raw = zone.get("radius", 100)
            zone_name = zone.get("name", "unknown")
            
            # Handle radius that might be string like "100m" or "100"
            if isinstance(zone_radius_raw, str):
                zone_radius = float(zone_radius_raw.replace('m', '').strip())
            else:
                zone_radius = float(zone_radius_raw) if zone_radius_raw else 100.0

            if zone_lat is None or zone_lon is None:
                _LOGGER.warning(f"Zone '{zone_name}' has no coordinates, skipping")
                continue

            # Calculate distance from device to zone center
            distance = self._calculate_distance(
                latitude, longitude, zone_lat, zone_lon
            )

            # Log zone check without exposing exact coordinates
            _LOGGER.debug(
                f"Zone '{zone_name}': distance={distance:.1f}m, radius={zone_radius}m"
            )
            
            # Track closest zone
            if distance < closest_distance:
                closest_distance = distance
                closest_zone = zone_name

            # Check if within zone radius
            if distance <= zone_radius:
                coords = format_coordinates(latitude, longitude, precision=5)
                _LOGGER.info(
                    f"Device at {coords} is in zone "
                    f"'{zone_name}' (distance: {distance:.1f}m, radius: {zone_radius}m)"
                )
                return True, zone_name

        coords = format_coordinates(latitude, longitude, precision=5)
        _LOGGER.info(
            f"Device at {coords} is not in any zone. "
            f"Closest: '{closest_zone}' at {closest_distance:.1f}m"
        )
        return False, None

    def update_zones(self, zones: List[Dict]):
        """Update zone list."""
        self.zones = zones
        _LOGGER.info(f"Updated zones: {len(zones)} zones")
