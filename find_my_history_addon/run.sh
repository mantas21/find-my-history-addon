#!/bin/bash
set -e

echo "Starting Find My Location History..."

# Read config from options.json (Home Assistant passes this)
CONFIG_PATH=/data/options.json

# Export configuration as environment variables
export HA_URL=$(jq -r '.ha_url' $CONFIG_PATH)
export HA_TOKEN=$(jq -r '.ha_token' $CONFIG_PATH)
export CHECK_INTERVAL=$(jq -r '.check_interval' $CONFIG_PATH)
export INFLUXDB_HOST=$(jq -r '.influxdb_host' $CONFIG_PATH)
export INFLUXDB_PORT=$(jq -r '.influxdb_port' $CONFIG_PATH)
export INFLUXDB_DATABASE=$(jq -r '.influxdb_database' $CONFIG_PATH)
export INFLUXDB_USERNAME=$(jq -r '.influxdb_username' $CONFIG_PATH)
export INFLUXDB_PASSWORD=$(jq -r '.influxdb_password' $CONFIG_PATH)
export FOCUS_UNKNOWN_LOCATIONS=$(jq -r '.focus_unknown_locations' $CONFIG_PATH)
export API_PORT=$(jq -r '.api_port' $CONFIG_PATH)
export DEVICES=$(jq -r '.devices | @json' $CONFIG_PATH)

echo "Configuration loaded"
echo "HA URL: ${HA_URL}"
echo "Check interval: ${CHECK_INTERVAL} minutes"
echo "InfluxDB: ${INFLUXDB_HOST}:${INFLUXDB_PORT}/${INFLUXDB_DATABASE}"
echo "API Port: ${API_PORT}"

# Start the Python application
cd /app
exec python3 -m find_my_history.main
