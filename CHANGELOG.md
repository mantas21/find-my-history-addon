# Changelog

## [1.0.0] - 2026-01-11

### Added
- Initial release
- Automatic location tracking from iCloud device trackers
- Zone detection using Home Assistant zones
- InfluxDB storage for historical data
- REST API for location history queries
- Custom Lovelace card with time slider
- Interactive map visualization with Leaflet.js
- Playback controls for reviewing location history
- Statistics API endpoint
- Focus on unknown locations feature
- Configurable polling interval
- Support for multiple devices
- Docker-based add-on architecture

### Features
- Polls device_tracker entities at configurable intervals (default: 30 minutes)
- Detects when devices are in known zones vs unknown locations
- Stores location data with tags and fields in InfluxDB
- Provides REST API for Lovelace card
- Interactive dashboard with time slider
- Color-coded markers (green=in zone, red=unknown)
- Playback feature to review location changes
- Statistics showing time in zones vs unknown locations

### Technical
- Python-based backend
- Flask API server
- InfluxDB 1.x and 2.x compatibility
- Home Assistant API integration
- Haversine formula for distance calculation
- Leaflet.js for map visualization
- Responsive Lovelace custom card
