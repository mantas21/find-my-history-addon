# Find My Location History - Home Assistant Add-on

Records and visualizes device location history from Apple's Find My (via Home Assistant iCloud integration) with a focus on tracking when devices are at unknown locations.

## Features

- 📍 **Automatic Location Tracking**: Polls device_tracker entities at configurable intervals
- 🗺️ **Zone Detection**: Identifies when devices are in known Home Assistant zones vs unknown locations
- 📊 **InfluxDB Storage**: Stores historical location data in InfluxDB for long-term analysis
- 🎨 **Interactive Dashboard**: Custom Lovelace card with time slider for reviewing location history
- 🔴 **Unknown Location Focus**: Highlights periods when devices are not in known zones
- 🔄 **Playback Feature**: Review location changes over time with playback controls
- 📈 **Statistics API**: View time spent in zones vs unknown locations

## Installation

### Method 1: Add Custom Repository (Recommended)

1. Go to **Supervisor** → **Add-on Store** → **⋮** (three dots) → **Repositories**
2. Add this repository URL: `https://github.com/mantas21/find-my-history-addon`
3. Find "Find My Location History" in the add-on store
4. Click **Install**

### Method 2: Local Installation

1. Copy this directory to `/addons/find_my_history/` on your Home Assistant system
2. Reload Supervisor
3. The add-on should appear in the local add-ons section

## Configuration

### Required Settings

```yaml
ha_url: "http://supervisor/core"
ha_token: "YOUR_LONG_LIVED_ACCESS_TOKEN"
devices:
  - device_tracker.iphone
  - device_tracker.ipad
influxdb_host: "a0d7b954_influxdb"
influxdb_port: 8086
influxdb_database: "find_my_history"
influxdb_username: "admin"
influxdb_password: "YOUR_INFLUXDB_PASSWORD"
```

### Getting Your Long-Lived Access Token

1. Go to Home Assistant → **Settings** → **People**
2. Scroll to **Long-lived access tokens**
3. Click **Create Token**
4. Name it: "Find My History Add-on"
5. Copy the token and paste it in the add-on configuration

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `ha_url` | string | `http://supervisor/core` | Home Assistant API URL |
| `ha_token` | string | *required* | Long-lived access token |
| `check_interval` | int | `30` | Polling interval in minutes |
| `devices` | list | `[]` | Device tracker entity IDs to track |
| `influxdb_host` | string | `a0d7b954_influxdb` | InfluxDB hostname |
| `influxdb_port` | int | `8086` | InfluxDB port |
| `influxdb_database` | string | `find_my_history` | Database name |
| `influxdb_username` | string | `admin` | InfluxDB username |
| `influxdb_password` | string | *required* | InfluxDB password |
| `focus_unknown_locations` | bool | `true` | Highlight unknown locations |
| `api_port` | int | `8090` | API server port |

## Prerequisites

### 1. iCloud Integration

- iCloud integration must be configured in Home Assistant
- Device trackers must be enabled and reporting locations
- Configure at: Settings → Devices & Services → iCloud

### 2. InfluxDB Add-on

- Install and configure InfluxDB add-on
- Create a database for location history (e.g., `find_my_history`)
- Note your username and password

### 3. Create InfluxDB Database

Via InfluxDB UI:
```
CREATE DATABASE find_my_history
```

Or via command line:
```bash
curl -X POST "http://a0d7b954_influxdb:8086/query" \
  --data-urlencode "q=CREATE DATABASE find_my_history"
```

## Usage

### Starting the Add-on

1. Configure the add-on with your credentials
2. Click **Start**
3. Check the **Log** tab to verify it's running
4. You should see messages like:
   - "Configuration loaded: X devices configured"
   - "Loaded X zones"
   - "Starting API server on port 8090"
   - "Stored location for device_tracker.xxx"

### Installing the Lovelace Card

1. Copy `www/find-my-history-card.js` to `/config/www/`
2. Go to Settings → Dashboards → Resources
3. Click **Add Resource**
4. URL: `/local/find-my-history-card.js`
5. Type: **JavaScript Module**
6. Click **Create**

### Adding the Card to Dashboard

```yaml
type: custom:find-my-history-card
devices:
  - device_tracker.iphone
  - device_tracker.ipad
default_time_range: 24h
highlight_unknown: true
api_url: http://localhost:8090
```

## API Endpoints

The add-on provides a REST API for the Lovelace card:

- `GET /api/health` - Health check
- `GET /api/devices` - List tracked devices
- `GET /api/zones` - List Home Assistant zones
- `GET /api/locations?device_id=xxx&start=xxx&end=xxx` - Get location history
- `GET /api/stats?device_id=xxx&start=xxx&end=xxx` - Get statistics

## Troubleshooting

### Add-on won't start

- Check configuration for required fields (ha_token, influxdb_password)
- Verify InfluxDB is running: `ha addons info a0d7b954_influxdb`
- Check logs: `ha addons logs local_find_my_history`

### No location data

- Verify devices are configured correctly
- Check iCloud integration is working
- Ensure device trackers have recent location updates
- Check InfluxDB database exists

### Card doesn't load

- Verify card file is in `/config/www/`
- Check browser console for errors
- Ensure card resource is added in Lovelace

## How It Works

1. **Polling**: The add-on polls device_tracker entities at the configured interval
2. **Zone Detection**: Compares device location with Home Assistant zones using Haversine formula
3. **Storage**: Stores location data in InfluxDB with tags (device_id, in_zone) and fields (lat, lon, accuracy)
4. **API**: Provides REST API for the Lovelace card to query historical data
5. **Visualization**: Lovelace card displays location history on a map with time slider

## Data Schema

```
measurement: device_location
tags:
  - device_id: device_tracker entity ID
  - device_name: friendly name
  - in_zone: true/false
  - zone_name: zone name if in_zone
fields:
  - latitude: float
  - longitude: float
  - accuracy: float (meters)
  - altitude: float (meters)
timestamp: location update time
```

## Privacy & Security

- All data is stored locally in your InfluxDB instance
- No data is sent to external services
- API runs on local network only
- Use strong passwords for InfluxDB
- Keep your long-lived access token secure

## Contributing

Contributions are welcome! Please open an issue or pull request.

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.

## Acknowledgments

- Home Assistant community
- InfluxDB
- Leaflet.js for map visualization
