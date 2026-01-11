"""Unit tests for device_prefs module."""

import pytest
import json
import os
import tempfile
from pathlib import Path
from find_my_history.device_prefs import DevicePreferences, get_device_prefs, DEFAULT_PREFS_PATH


class TestDevicePreferences:
    """Test DevicePreferences class."""

    def test_init_creates_default_prefs(self):
        """Test initialization with no existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prefs_path = os.path.join(tmpdir, "prefs.json")
            prefs = DevicePreferences(prefs_path)
            
            assert prefs.get_tracked_devices() == []
            assert not prefs.is_tracked("device_tracker.iphone")

    def test_load_existing_prefs(self):
        """Test loading existing preferences from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prefs_path = os.path.join(tmpdir, "prefs.json")
            
            # Create existing prefs file
            existing_data = {
                "tracked_devices": ["device_tracker.iphone"],
                "device_intervals": {"device_tracker.iphone": 5}
            }
            with open(prefs_path, 'w') as f:
                json.dump(existing_data, f)
            
            prefs = DevicePreferences(prefs_path)
            assert prefs.is_tracked("device_tracker.iphone")
            assert prefs.get_interval("device_tracker.iphone") == 5

    def test_add_device(self):
        """Test adding a device to tracking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prefs_path = os.path.join(tmpdir, "prefs.json")
            prefs = DevicePreferences(prefs_path)
            
            result = prefs.add_device("device_tracker.iphone", interval_minutes=10)
            assert result is True
            assert prefs.is_tracked("device_tracker.iphone")
            assert prefs.get_interval("device_tracker.iphone") == 10

    def test_add_device_already_tracked(self):
        """Test adding a device that's already tracked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prefs_path = os.path.join(tmpdir, "prefs.json")
            prefs = DevicePreferences(prefs_path)
            
            prefs.add_device("device_tracker.iphone", interval_minutes=5)
            result = prefs.add_device("device_tracker.iphone", interval_minutes=10)
            
            assert result is False
            assert prefs.get_interval("device_tracker.iphone") == 5  # Original interval

    def test_remove_device(self):
        """Test removing a device from tracking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prefs_path = os.path.join(tmpdir, "prefs.json")
            prefs = DevicePreferences(prefs_path)
            
            prefs.add_device("device_tracker.iphone")
            result = prefs.remove_device("device_tracker.iphone")
            
            assert result is True
            assert not prefs.is_tracked("device_tracker.iphone")

    def test_remove_device_not_tracked(self):
        """Test removing a device that's not tracked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prefs_path = os.path.join(tmpdir, "prefs.json")
            prefs = DevicePreferences(prefs_path)
            
            result = prefs.remove_device("device_tracker.iphone")
            assert result is False

    def test_toggle_device(self):
        """Test toggling device tracking status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prefs_path = os.path.join(tmpdir, "prefs.json")
            prefs = DevicePreferences(prefs_path)
            
            # Toggle on
            result = prefs.toggle_device("device_tracker.iphone", interval_minutes=5)
            assert result is True
            assert prefs.is_tracked("device_tracker.iphone")
            
            # Toggle off
            result = prefs.toggle_device("device_tracker.iphone")
            assert result is False
            assert not prefs.is_tracked("device_tracker.iphone")

    def test_get_interval_default(self):
        """Test getting interval with default value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prefs_path = os.path.join(tmpdir, "prefs.json")
            prefs = DevicePreferences(prefs_path)
            
            # Device not tracked, should return default
            interval = prefs.get_interval("device_tracker.iphone", default=10)
            assert interval == 10

    def test_set_interval(self):
        """Test setting interval for a device."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prefs_path = os.path.join(tmpdir, "prefs.json")
            prefs = DevicePreferences(prefs_path)
            
            prefs.add_device("device_tracker.iphone", interval_minutes=5)
            prefs.set_interval("device_tracker.iphone", interval_minutes=15)
            
            assert prefs.get_interval("device_tracker.iphone") == 15

    def test_get_tracked_with_intervals(self):
        """Test getting tracked devices with intervals."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prefs_path = os.path.join(tmpdir, "prefs.json")
            prefs = DevicePreferences(prefs_path)
            
            prefs.add_device("device_tracker.iphone", interval_minutes=5)
            prefs.add_device("device_tracker.ipad", interval_minutes=10)
            
            tracked = prefs.get_tracked_with_intervals()
            assert len(tracked) == 2
            assert tracked[0]["entity_id"] == "device_tracker.iphone"
            assert tracked[0]["interval_minutes"] == 5
            assert tracked[0]["enabled"] is True

    def test_persistence(self):
        """Test that preferences persist across instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prefs_path = os.path.join(tmpdir, "prefs.json")
            
            # Create first instance and add device
            prefs1 = DevicePreferences(prefs_path)
            prefs1.add_device("device_tracker.iphone", interval_minutes=10)
            
            # Create second instance and verify
            prefs2 = DevicePreferences(prefs_path)
            assert prefs2.is_tracked("device_tracker.iphone")
            assert prefs2.get_interval("device_tracker.iphone") == 10

    def test_reload(self):
        """Test reloading preferences from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prefs_path = os.path.join(tmpdir, "prefs.json")
            prefs = DevicePreferences(prefs_path)
            
            # Add device
            prefs.add_device("device_tracker.iphone")
            
            # Manually modify file
            with open(prefs_path, 'r') as f:
                data = json.load(f)
            data["tracked_devices"] = ["device_tracker.ipad"]
            with open(prefs_path, 'w') as f:
                json.dump(data, f)
            
            # Reload and verify
            prefs.reload()
            assert not prefs.is_tracked("device_tracker.iphone")
            assert prefs.is_tracked("device_tracker.ipad")

    def test_invalid_json_handling(self):
        """Test handling of invalid JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prefs_path = os.path.join(tmpdir, "prefs.json")
            
            # Write invalid JSON
            with open(prefs_path, 'w') as f:
                f.write("invalid json{")
            
            # Should not crash, should use defaults
            prefs = DevicePreferences(prefs_path)
            assert prefs.get_tracked_devices() == []

    def test_get_device_prefs_singleton(self):
        """Test get_device_prefs returns singleton instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prefs_path = os.path.join(tmpdir, "prefs.json")
            
            prefs1 = get_device_prefs(prefs_path)
            prefs2 = get_device_prefs(prefs_path)
            
            # Should be the same instance
            assert prefs1 is prefs2
