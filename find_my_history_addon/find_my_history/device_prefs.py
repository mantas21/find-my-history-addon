"""Device preferences manager for persistent tracking configuration."""

import json
import logging
import os
from typing import Dict, List, Optional
from threading import Lock

_LOGGER = logging.getLogger(__name__)

# Default path for preferences file (persists in add-on /data volume)
DEFAULT_PREFS_PATH = "/data/tracked_devices.json"


class DevicePreferences:
    """Manages device tracking preferences with persistent storage."""

    def __init__(self, prefs_path: str = DEFAULT_PREFS_PATH):
        """
        Initialize device preferences manager.

        Args:
            prefs_path: Path to the preferences JSON file
        """
        self.prefs_path = prefs_path
        self._lock = Lock()
        self._cache: Dict = {}
        self._load()

    def _load(self) -> None:
        """Load preferences from file."""
        with self._lock:
            if os.path.exists(self.prefs_path):
                try:
                    with open(self.prefs_path, 'r') as f:
                        self._cache = json.load(f)
                    _LOGGER.info(f"Loaded device preferences from {self.prefs_path}")
                except (json.JSONDecodeError, IOError) as e:
                    _LOGGER.warning(f"Could not load preferences: {e}")
                    self._cache = {"tracked_devices": [], "device_intervals": {}}
            else:
                _LOGGER.info("No preferences file found, using defaults")
                self._cache = {"tracked_devices": [], "device_intervals": {}}

    def _save(self) -> None:
        """Save preferences to file."""
        with self._lock:
            try:
                # Ensure directory exists
                os.makedirs(os.path.dirname(self.prefs_path), exist_ok=True)
                with open(self.prefs_path, 'w') as f:
                    json.dump(self._cache, f, indent=2)
                _LOGGER.debug(f"Saved device preferences to {self.prefs_path}")
            except IOError as e:
                _LOGGER.error(f"Could not save preferences: {e}")

    def get_tracked_devices(self) -> List[str]:
        """
        Get list of tracked device entity IDs.

        Returns:
            List of entity_id strings that are being tracked
        """
        with self._lock:
            return list(self._cache.get("tracked_devices", []))

    def is_tracked(self, entity_id: str) -> bool:
        """
        Check if a device is being tracked.

        Args:
            entity_id: Device entity ID

        Returns:
            True if device is tracked, False otherwise
        """
        with self._lock:
            return entity_id in self._cache.get("tracked_devices", [])

    def add_device(self, entity_id: str, interval_minutes: int = 5) -> bool:
        """
        Add a device to tracking.

        Args:
            entity_id: Device entity ID to track
            interval_minutes: Polling interval in minutes

        Returns:
            True if device was added, False if already tracked
        """
        with self._lock:
            tracked = self._cache.setdefault("tracked_devices", [])
            intervals = self._cache.setdefault("device_intervals", {})
            
            if entity_id in tracked:
                _LOGGER.debug(f"Device {entity_id} already tracked")
                return False
            
            tracked.append(entity_id)
            intervals[entity_id] = interval_minutes
            _LOGGER.info(f"Added device {entity_id} to tracking (interval: {interval_minutes}m)")
        
        self._save()
        return True

    def remove_device(self, entity_id: str) -> bool:
        """
        Remove a device from tracking.

        Args:
            entity_id: Device entity ID to stop tracking

        Returns:
            True if device was removed, False if not found
        """
        with self._lock:
            tracked = self._cache.get("tracked_devices", [])
            intervals = self._cache.get("device_intervals", {})
            
            if entity_id not in tracked:
                _LOGGER.debug(f"Device {entity_id} was not tracked")
                return False
            
            tracked.remove(entity_id)
            intervals.pop(entity_id, None)
            _LOGGER.info(f"Removed device {entity_id} from tracking")
        
        self._save()
        return True

    def toggle_device(self, entity_id: str, interval_minutes: int = 5) -> bool:
        """
        Toggle device tracking status.

        Args:
            entity_id: Device entity ID
            interval_minutes: Polling interval if adding

        Returns:
            True if device is now tracked, False if now untracked
        """
        if self.is_tracked(entity_id):
            self.remove_device(entity_id)
            return False
        else:
            self.add_device(entity_id, interval_minutes)
            return True

    def get_interval(self, entity_id: str, default: int = 5) -> int:
        """
        Get polling interval for a device.

        Args:
            entity_id: Device entity ID
            default: Default interval if not set

        Returns:
            Interval in minutes
        """
        with self._lock:
            return self._cache.get("device_intervals", {}).get(entity_id, default)

    def set_interval(self, entity_id: str, interval_minutes: int) -> None:
        """
        Set polling interval for a device.

        Args:
            entity_id: Device entity ID
            interval_minutes: New interval in minutes
        """
        with self._lock:
            intervals = self._cache.setdefault("device_intervals", {})
            intervals[entity_id] = interval_minutes
        self._save()

    def get_tracked_with_intervals(self) -> List[Dict]:
        """
        Get tracked devices with their intervals.

        Returns:
            List of dicts with entity_id and interval_minutes
        """
        with self._lock:
            tracked = self._cache.get("tracked_devices", [])
            intervals = self._cache.get("device_intervals", {})
            return [
                {
                    "entity_id": entity_id,
                    "interval_minutes": intervals.get(entity_id, 5),
                    "enabled": True
                }
                for entity_id in tracked
            ]

    def reload(self) -> None:
        """Reload preferences from file."""
        self._load()


# Global instance for shared access
_instance: Optional[DevicePreferences] = None


def get_device_prefs(prefs_path: str = DEFAULT_PREFS_PATH) -> DevicePreferences:
    """
    Get the global device preferences instance.

    Args:
        prefs_path: Path to preferences file

    Returns:
        DevicePreferences instance
    """
    global _instance
    if _instance is None:
        _instance = DevicePreferences(prefs_path)
    return _instance
