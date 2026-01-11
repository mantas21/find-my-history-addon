"""Unit tests for log_utils module."""

import pytest
from find_my_history.log_utils import format_coordinates, setup_secure_logging


class TestLogUtils:
    """Test logging utilities."""

    def test_format_coordinates_default_precision(self):
        """Test coordinate formatting with default precision."""
        result = format_coordinates(54.8985123, 23.9036789)
        assert "54.89851" in result
        assert "23.90368" in result

    def test_format_coordinates_custom_precision(self):
        """Test coordinate formatting with custom precision."""
        result = format_coordinates(54.8985123, 23.9036789, precision=3)
        assert "54.899" in result
        assert "23.904" in result

    def test_format_coordinates_none_values(self):
        """Test coordinate formatting with None values."""
        result = format_coordinates(None, None)
        assert "None" in result or "N/A" in result

    def test_format_coordinates_zero(self):
        """Test coordinate formatting with zero values."""
        result = format_coordinates(0.0, 0.0)
        assert "0.0" in result or "0.00000" in result

    def test_setup_secure_logging(self):
        """Test secure logging setup."""
        # Should not raise exception
        setup_secure_logging(level=20)  # INFO level
        assert True  # If we get here, setup worked
