"""Utility functions for safe logging of sensitive information."""

import logging
import os
import re
from typing import Any, Dict, Optional

_LOGGER = logging.getLogger(__name__)

# Environment variable to control sensitive data masking in logs
# Set to 'true' to mask sensitive data, 'false' to show full details
MASK_SENSITIVE_DATA = os.environ.get("MASK_SENSITIVE_LOGS", "false").lower() == "true"


def format_coordinates(latitude: Optional[float], longitude: Optional[float], precision: int = 5) -> str:
    """
    Format coordinates for logging with meter-level precision.
    
    Args:
        latitude: Latitude value
        longitude: Longitude value
        precision: Decimal places (default 5 for meter-level precision)
        
    Returns:
        Formatted coordinate string with full precision
    """
    if latitude is None or longitude is None:
        return "(N/A, N/A)"
    
    # Keep meter-level precision (5 decimal places = ~1.1m precision)
    return f"({latitude:.{precision}f}, {longitude:.{precision}f})"


def sanitize_token(token: Optional[str], visible_chars: int = 4) -> str:
    """
    Sanitize authentication tokens for logging.
    
    Args:
        token: Token string to sanitize
        visible_chars: Number of characters to show at the start
        
    Returns:
        Sanitized token string (e.g., "abcd...")
    """
    if not token:
        return "***"
    
    if len(token) <= visible_chars:
        return "***"
    
    return f"{token[:visible_chars]}..."


def sanitize_password(password: Optional[str]) -> str:
    """
    Sanitize passwords for logging.
    
    Args:
        password: Password string to sanitize
        
    Returns:
        Always returns "***" regardless of input
    """
    if password:
        return "***"
    return "***"


def sanitize_entity_id(entity_id: Optional[str]) -> str:
    """
    Sanitize entity IDs - these are generally safe but can be sanitized
    if they contain sensitive information.
    
    Args:
        entity_id: Entity ID string
        
    Returns:
        Entity ID (currently returned as-is, but can be modified if needed)
    """
    if not entity_id:
        return "N/A"
    return entity_id


class SecureLogFormatter(logging.Formatter):
    """
    Log formatter that can mask sensitive information in log messages.
    
    Masks:
    - GPS coordinates (latitude, longitude patterns)
    - Authentication tokens
    - Passwords
    """
    
    # Pattern to match coordinate pairs like (12.34567, -98.76543)
    COORD_PATTERN = re.compile(r'\((-?\d+\.\d{4,}),\s*(-?\d+\.\d{4,})\)')
    
    # Pattern to match tokens (long alphanumeric strings)
    TOKEN_PATTERN = re.compile(r'\b([a-zA-Z0-9]{20,})\b')
    
    def __init__(self, fmt=None, datefmt=None, mask_sensitive=True):
        """
        Initialize secure log formatter.
        
        Args:
            fmt: Log format string
            datefmt: Date format string
            mask_sensitive: If True, mask sensitive data in logs
        """
        super().__init__(fmt, datefmt)
        self.mask_sensitive = mask_sensitive
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record, masking sensitive data if enabled."""
        # Get the formatted message
        message = super().format(record)
        
        if not self.mask_sensitive:
            return message
        
        # Mask coordinates: replace with masked version
        # Keep first 2 decimal places for approximate location (~1km precision)
        def mask_coords(match):
            lat = float(match.group(1))
            lon = float(match.group(2))
            # Show approximate location but mask precise coordinates
            return f"({lat:.2f}**, {lon:.2f}**)"
        
        message = self.COORD_PATTERN.sub(mask_coords, message)
        
        # Mask tokens (keep first 4 chars)
        def mask_token(match):
            token = match.group(1)
            if len(token) > 4:
                return f"{token[:4]}***"
            return "***"
        
        # Only mask tokens that look like auth tokens (not entity IDs or device names)
        # Entity IDs typically have dots, device names have spaces - tokens don't
        def mask_token_safe(match):
            token = match.group(1)
            # Don't mask if it contains dots or spaces (likely not a token)
            if '.' in token or ' ' in token:
                return token
            if len(token) > 4:
                return f"{token[:4]}***"
            return "***"
        
        message = self.TOKEN_PATTERN.sub(mask_token_safe, message)
        
        return message


def setup_secure_logging(level=logging.INFO, mask_sensitive=None):
    """
    Set up secure logging configuration.
    
    Args:
        level: Logging level
        mask_sensitive: Whether to mask sensitive data (defaults to MASK_SENSITIVE_DATA env var)
    """
    if mask_sensitive is None:
        mask_sensitive = MASK_SENSITIVE_DATA
    
    # Create secure formatter
    formatter = SecureLogFormatter(
        fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        mask_sensitive=mask_sensitive
    )
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler with secure formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    return root_logger
