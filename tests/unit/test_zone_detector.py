"""Unit tests for zone_detector module."""

import pytest
from find_my_history.zone_detector import ZoneDetector


class TestZoneDetector:
    """Test ZoneDetector class."""

    def test_init_with_zones(self, sample_zones):
        """Test initialization with zones."""
        detector = ZoneDetector(sample_zones)
        assert len(detector.zones) == 3
        assert detector.zones[0]["name"] == "home"

    def test_init_with_empty_zones(self):
        """Test initialization with empty zones."""
        detector = ZoneDetector([])
        assert len(detector.zones) == 0

    def test_check_zone_inside_radius(self, sample_zones):
        """Test zone detection when device is inside zone radius."""
        detector = ZoneDetector(sample_zones)
        
        # Device at home zone center
        in_zone, zone_name = detector.check_zone(54.8985, 23.9036)
        assert in_zone is True
        assert zone_name == "home"

    def test_check_zone_outside_radius(self, sample_zones):
        """Test zone detection when device is outside all zones."""
        detector = ZoneDetector(sample_zones)
        
        # Device far from any zone
        in_zone, zone_name = detector.check_zone(55.0000, 24.0000)
        assert in_zone is False
        assert zone_name is None

    def test_check_zone_at_boundary(self, sample_zones):
        """Test zone detection at zone boundary."""
        detector = ZoneDetector(sample_zones)
        
        # Device exactly at 100m radius from home (edge case)
        # Using approximate coordinates for boundary test
        in_zone, zone_name = detector.check_zone(54.8990, 23.9036)
        assert in_zone is True
        assert zone_name == "home"

    def test_check_zone_no_zones(self):
        """Test zone detection with no zones configured."""
        detector = ZoneDetector([])
        in_zone, zone_name = detector.check_zone(54.8985, 23.9036)
        assert in_zone is False
        assert zone_name is None

    def test_check_zone_multiple_zones_closest(self, sample_zones):
        """Test zone detection when device is in multiple zones (should return first match)."""
        # Create overlapping zones
        zones = [
            {"name": "zone1", "latitude": 54.8985, "longitude": 23.9036, "radius": 200},
            {"name": "zone2", "latitude": 54.8985, "longitude": 23.9036, "radius": 150},
        ]
        detector = ZoneDetector(zones)
        
        # Device at center of both zones
        in_zone, zone_name = detector.check_zone(54.8985, 23.9036)
        assert in_zone is True
        assert zone_name == "zone1"  # First match

    def test_check_zone_string_radius(self):
        """Test zone detection with string radius value."""
        zones = [
            {"name": "home", "latitude": 54.8985, "longitude": 23.9036, "radius": "100m"},
        ]
        detector = ZoneDetector(zones)
        
        in_zone, zone_name = detector.check_zone(54.8985, 23.9036)
        assert in_zone is True
        assert zone_name == "home"

    def test_check_zone_invalid_coordinates(self, sample_zones):
        """Test zone detection with invalid zone coordinates."""
        zones = [
            {"name": "invalid", "latitude": None, "longitude": None, "radius": 100},
        ]
        detector = ZoneDetector(zones)
        
        # Should not crash, just return not in zone
        in_zone, zone_name = detector.check_zone(54.8985, 23.9036)
        assert in_zone is False
        assert zone_name is None

    def test_update_zones(self, sample_zones):
        """Test updating zones."""
        detector = ZoneDetector(sample_zones)
        assert len(detector.zones) == 3
        
        new_zones = [{"name": "new_zone", "latitude": 55.0, "longitude": 25.0, "radius": 50}]
        detector.update_zones(new_zones)
        assert len(detector.zones) == 1
        assert detector.zones[0]["name"] == "new_zone"

    def test_distance_calculation_accuracy(self, sample_zones):
        """Test Haversine distance calculation accuracy."""
        detector = ZoneDetector(sample_zones)
        
        # Calculate distance between two known points
        # Home: 54.8985, 23.9036
        # Work: 54.6872, 25.2797
        # Approximate distance: ~91km
        distance = detector._calculate_distance(54.8985, 23.9036, 54.6872, 25.2797)
        
        # Should be approximately 91km (allowing 5% error)
        assert 86000 < distance < 96000

    def test_distance_calculation_same_point(self, sample_zones):
        """Test distance calculation for same point."""
        detector = ZoneDetector(sample_zones)
        
        distance = detector._calculate_distance(54.8985, 23.9036, 54.8985, 23.9036)
        assert distance == pytest.approx(0, abs=1)  # Should be 0 (within 1m)

    @pytest.mark.parametrize("lat,lon,expected_zone", [
        (54.8985, 23.9036, "home"),  # At home center
        (54.6872, 25.2797, "work"),  # At work center
        (55.0000, 24.0000, None),    # Outside all zones
    ])
    def test_check_zone_parametrized(self, sample_zones, lat, lon, expected_zone):
        """Parametrized test for zone detection."""
        detector = ZoneDetector(sample_zones)
        in_zone, zone_name = detector.check_zone(lat, lon)
        
        if expected_zone:
            assert in_zone is True
            assert zone_name == expected_zone
        else:
            assert in_zone is False
            assert zone_name is None
