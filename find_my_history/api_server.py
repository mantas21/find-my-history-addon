"""API server entry point that runs alongside main service."""

import asyncio
import logging
import os
import sys

import bashio

from find_my_history.ha_client import HomeAssistantClient
from find_my_history.influxdb_client import InfluxDBLocationClient
from find_my_history.api import LocationHistoryAPI

_LOGGER = logging.getLogger(__name__)


def load_config() -> dict:
    """Load configuration from Home Assistant add-on options."""
    config = {
        "ha_url": bashio.config.get("ha_url", "http://supervisor/core"),
        "ha_token": bashio.config.get("ha_token"),
        "influxdb_host": bashio.config.get("influxdb_host", "a0d7b954_influxdb"),
        "influxdb_port": bashio.config.get("influxdb_port", 8086),
        "influxdb_database": bashio.config.get("influxdb_database", "find_my_history"),
        "influxdb_username": bashio.config.get("influxdb_username", "admin"),
        "influxdb_password": bashio.config.get("influxdb_password"),
        "api_port": int(bashio.config.get("api_port", 8080)),
    }

    if not config["ha_token"]:
        _LOGGER.error("ha_token is required in add-on configuration")
        sys.exit(1)

    return config


async def main():
    """Main entry point for API server."""
    _LOGGER.info("Starting Find My Location History API server...")

    config = load_config()

    # Initialize clients
    ha_client = HomeAssistantClient(config["ha_url"], config["ha_token"])
    influx_client = InfluxDBLocationClient(
        host=config["influxdb_host"],
        port=config["influxdb_port"],
        database=config["influxdb_database"],
        username=config["influxdb_username"],
        password=config["influxdb_password"]
    )

    # Create and run API server
    api = LocationHistoryAPI(ha_client, influx_client, port=config["api_port"])
    await api.run()

    # Keep running
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        _LOGGER.info("Received interrupt signal, shutting down...")
    finally:
        influx_client.close()


if __name__ == "__main__":
    asyncio.run(main())
