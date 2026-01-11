# Find My Location History - Home Assistant Add-on

📱 **Apple Find My style location tracking** for Home Assistant. Record and visualize device location history from iCloud integration with a beautiful, intuitive interface.

![Version](https://img.shields.io/badge/version-0.9.2-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

### 🎨 Apple-Style UI
- **Sidebar Layout**: Clean sidebar with device list and details panel
- **Full-Width Map**: Unobstructed map view with minimal popups
- **Dark Theme**: iOS-inspired dark mode design
- **Draggable Devices**: Reorder tracked devices with drag & drop
- **Responsive Design**: Mobile-friendly with bottom sheet on small screens

### 📍 Location Tracking
- **Automatic Polling**: Configurable intervals per device (1-1440 minutes)
- **Zone Detection**: Identifies known Home Assistant zones vs unknown locations
- **Battery Tracking**: Shows device battery level and charging status
- **Location Details**: Business names, street addresses via OpenStreetMap
- **Duration Calculation**: Shows time spent at each location

### 🗺️ Interactive Map
- **Time Navigation**: Compact timeline slider with visual progress indicator
- **Playback Mode**: Animate through location history
- **Heatmap View**: Visualize time spent at locations
- **Layer Options**: Street map, satellite, dark theme
- **Smart Markers**: Size-based on recency (recent = larger, older = smaller)
- **Current Position**: Blue pulsing marker clearly distinguishes current location

### 📊 Data Management
- **InfluxDB Storage**: Long-term historical data storage
- **Update Now**: Force immediate location refresh
- **Time Range Selection**: View last hour, 6h, 24h, 7d, or 30d
- **Statistics**: Track known vs unknown location time

### 🔄 Device Management
- **UI-Based Tracking**: Add/remove devices from the web interface
- **Per-Device Intervals**: Configure different polling intervals per device
- **Persistent Preferences**: Device settings survive restarts
- **State Indicators**: Visual status (home/away) for each device

## 📸 Screenshots

*Sidebar layout with device list, details panel, and full-width map*

## 🚀 Installation

### Method 1: Add Custom Repository (Recommended)

1. Go to **Supervisor** → **Add-on Store** → **⋮** (three dots) → **Repositories**
2. Add this repository URL: `https://github.com/mantas21/find-my-history-addon`
3. Find **"Find My Location History"** in the add-on store
4. Click **Install**

### Method 2: Local Installation

1. Copy this directory to `/addons/find_my_history/` on your Home Assistant system
2. Reload Supervisor
3. The add-on should appear in the local add-ons section

## ⚙️ Configuration

### Quick Start

1. **Install InfluxDB Add-on** (if not already installed)
2. **Configure the add-on**:
   - Set `influxdb_host` (default: `a0d7b954-influxdb`)
   - Set `influxdb_password`
   - Add devices via the web UI (no need to configure in YAML)
3. **Start the add-on**
4. **Access the UI**: Click "Open Web UI" or go to Sidebar → Location History

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `ha_url` | string | `http://supervisor/core` | Home Assistant API URL |
| `ha_token` | string | *auto* | Auto-detected from Supervisor (or set manually) |
| `default_interval` | int | `5` | Default polling interval in minutes |
| `tracked_devices` | list | `[]` | Device tracker entity IDs (can be managed via UI) |
| `influxdb_host` | string | `a0d7b954-influxdb` | InfluxDB hostname |
| `influxdb_port` | int | `8086` | InfluxDB port |
| `influxdb_database` | string | `find_my_history` | Database name |
| `influxdb_username` | string | `admin` | InfluxDB username |
| `influxdb_password` | string | *required* | InfluxDB password |
| `focus_unknown_locations` | bool | `true` | Highlight unknown locations |
| `api_port` | int | `8090` | API server port |

### Getting Your Long-Lived Access Token (Optional)

If auto-detection doesn't work:

1. Go to Home Assistant → **Settings** → **People**
2. Scroll to **Long-lived access tokens**
3. Click **Create Token**
4. Name it: "Find My History Add-on"
5. Copy the token and paste it in the add-on configuration

## 📋 Prerequisites

### 1. iCloud Integration

- iCloud integration must be configured in Home Assistant
- Device trackers must be enabled and reporting locations
- Configure at: **Settings** → **Devices & Services** → **iCloud**

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
curl -X POST "http://a0d7b954-influxdb:8086/query" \
  --data-urlencode "q=CREATE DATABASE find_my_history"
```

## 🎯 Usage

### Starting the Add-on

1. Configure the add-on with your InfluxDB credentials
2. Click **Start**
3. Check the **Log** tab to verify it's running
4. You should see messages like:
   - "Configuration loaded: X devices configured"
   - "Loaded X zones"
   - "Starting API server on port 8090"
   - "Stored location for device_tracker.xxx"

### Using the Web UI

1. **Access**: Click "Open Web UI" from the add-on page, or go to **Sidebar** → **Location History**
2. **Add Devices**: Click "+ Add Device" button in the sidebar
3. **Select Device**: Click on a device chip to view its location history
4. **Navigate Time**: Use the timeline slider at the bottom of the map
5. **Playback**: Click the play button to animate through location history
6. **View Details**: Device details appear in the sidebar (location, time, battery, etc.)

### Device Management

- **Add Device**: Click "+ Add Device" → Select from available devices
- **Remove Device**: Hover over device chip → Click ✕ button
- **Reorder Devices**: Drag device chips to reorder (order persists)
- **Update Location**: Click "Update Now" button in device details

## 🔌 API Endpoints

The add-on provides a REST API:

- `GET /api/health` - Health check
- `GET /api/devices` - List all device trackers with tracking status
- `GET /api/zones` - List Home Assistant zones
- `GET /api/locations?device_id=xxx&start=xxx&end=xxx&limit=xxx` - Get location history
- `GET /api/stats?device_id=xxx&start=xxx&end=xxx` - Get statistics
- `POST /api/devices/toggle` - Toggle device tracking
- `POST /api/devices/update` - Force location update for a device

## 🐛 Troubleshooting

### Add-on won't start

- Check configuration for required fields (`influxdb_password`)
- Verify InfluxDB is running: `ha addons info a0d7b954-influxdb`
- Check logs: `ha addons logs 274754fd_find_my_history`
- Ensure `homeassistant_api: true` is set (should be automatic)

### No location data

- Verify devices are added via the web UI
- Check iCloud integration is working
- Ensure device trackers have recent location updates
- Check InfluxDB database exists
- Verify InfluxDB credentials are correct

### UI doesn't load

- Check add-on logs for errors
- Verify Ingress is enabled (should be automatic)
- Try accessing via `http://homeassistant:8090` directly
- Check browser console for JavaScript errors

### Devices not appearing

- Ensure device trackers exist in Home Assistant
- Check that device_tracker entities start with `device_tracker.`
- Verify iCloud integration is reporting locations
- Check add-on logs for API errors

## 🏗️ How It Works

1. **Polling**: The add-on polls device_tracker entities at configured intervals
2. **Zone Detection**: Compares device location with Home Assistant zones using Haversine formula
3. **Storage**: Stores location data in InfluxDB with tags and fields
4. **API**: Provides REST API for the web UI to query historical data
5. **Visualization**: Web UI displays location history on a map with interactive timeline

## 📊 Data Schema

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
  - battery_level: int (0-100)
  - battery_state: string ("charging" or "not_charging")
timestamp: location update time
```

## 🔒 Privacy & Security

- ✅ All data is stored locally in your InfluxDB instance
- ✅ No data is sent to external services
- ✅ API runs on local network only
- ✅ Use strong passwords for InfluxDB
- ✅ Location lookups use free OpenStreetMap services (optional)

## 🛠️ Technical Details

- **Backend**: Python 3 with aiohttp
- **Database**: InfluxDB 1.x and 2.x compatible
- **Frontend**: Vanilla JavaScript, Leaflet.js for maps
- **Architecture**: Home Assistant Add-on with S6 overlay
- **API**: RESTful API with CORS support

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

### Recent Updates (v0.9.x)

- ✨ Apple Find My style sidebar layout
- 🎨 Complete UI redesign with dark theme
- 🔋 Battery level tracking and display
- 📍 Enhanced location details (business names, addresses)
- 🗺️ Improved marker distinction (size-based on recency)
- ⏱️ Compact timeline navigation
- 📱 Responsive mobile layout

## 🤝 Contributing

Contributions are welcome! Please open an issue or pull request.

## 📄 License

MIT License

## 💬 Support

For issues and questions, please open an issue on [GitHub](https://github.com/mantas21/find-my-history-addon/issues).

## 🙏 Acknowledgments

- Home Assistant community
- InfluxDB
- Leaflet.js for map visualization
- OpenStreetMap for location data
- Apple for design inspiration

---

**Made with ❤️ for the Home Assistant community**
