"""Home Assistant API client for querying device trackers and zones."""

import requests
import logging
from typing import Dict, List, Optional, Any

_LOGGER = logging.getLogger(__name__)


class HomeAssistantClient:
    """Client for interacting with Home Assistant REST API."""

    def __init__(self, base_url: str, token: str):
        """
        Initialize Home Assistant client.

        Args:
            base_url: Home Assistant base URL (e.g., http://supervisor/core)
            token: Long-lived access token
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def _request(self, method: str, endpoint: str, **kwargs) -> Optional[Any]:
        """Make HTTP request to Home Assistant API."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method, url, headers=self.headers, timeout=10, **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            _LOGGER.error(f"HA API request failed: {e}")
            return None

    def get_device_tracker_state(self, entity_id: str) -> Optional[Dict]:
        """
        Get state of a device_tracker entity.

        Args:
            entity_id: Entity ID (e.g., device_tracker.mantas_s_iphone)

        Returns:
            Entity state dict or None if error
        """
        return self._request("GET", f"/api/states/{entity_id}")

    def get_all_device_trackers(self) -> List[Dict]:
        """
        Get all device_tracker entities.

        Returns:
            List of device_tracker entity states
        """
        states = self._request("GET", "/api/states")
        if not states:
            return []

        return [
            state for state in states
            if state.get("entity_id", "").startswith("device_tracker.")
        ]

    def get_zones(self) -> List[Dict]:
        """
        Get all Home Assistant zones.

        Returns:
            List of zone configurations
        """
        zones = self._request("GET", "/api/config/zone_registry")
        if not zones:
            return []
        return zones

    def get_entity_state(self, entity_id: str) -> Optional[Dict]:
        """
        Get state of any entity.

        Args:
            entity_id: Entity ID

        Returns:
            Entity state dict or None
        """
        return self._request("GET", f"/api/states/{entity_id}")
