# Changelog

All notable changes to this project will be documented in this file.

## [0.9.2] - 2025-01-XX

### Fixed
- Timeline slider styling - removed duplicate CSS, properly centered thumb
- Removed time markers (start/end) from below timeline
- Fixed slider thumb centering on track
- Marker sizing based on recency (last location: 12px, older: progressively smaller)
- Improved visual distinction between current and past locations

## [0.9.1] - 2025-01-XX

### Fixed
- Added visual progress bar (blue) to timeline slider
- Current marker always blue with pulsing animation
- Past markers grey/faded and smaller
- Fixed duplicate markers issue
- Improved time display formatting

## [0.9.0] - 2025-01-XX

### Added
- **Apple Find My style sidebar layout** - Complete UI redesign
- Sidebar with device list and details panel
- Full-width map (no popup-heavy interface)
- Draggable device chips with reorder persistence
- Minimal map popups (just device name + time)
- Compact time navigation overlay at bottom of map
- Map/Satellite layer switcher with Apple Maps style
- Heatmap toggle as floating control
- Add Device modal for adding new devices
- Responsive layout: sidebar becomes bottom sheet on mobile
- Apple design language: dark theme, blur effects, SF Pro typography

### Changed
- Complete UI overhaul from popup-based to sidebar-based
- Device management moved to web UI (no YAML config needed)
- First device auto-selected on page load
- Device order persists in localStorage

## [0.8.0] - 2025-01-XX

### Added
- **Battery level tracking** - Extract and store battery data from device_tracker
- **Battery display** - Apple-style color coding (green/yellow/red)
- **Charging indicator** - ⚡ icon with pulse animation
- **Update Now button** - Force immediate location refresh
- **Toast notifications** - Apple-style success/error feedback
- **Last updated timestamp** - Relative time display in popup
- **Enhanced popup** - Complete redesign with battery section

### Changed
- Complete Apple-style UI redesign (iOS dark mode)
- Popup structure with proper sections and dividers
- Color scheme following Apple system colors
- Typography using SF Pro style fonts

## [0.7.4] - 2025-01-XX

### Fixed
- Moved heatmap control to bottom-left (no overlap with layer control)
- Reverted popup offset to default Leaflet positioning

## [0.7.3] - 2025-01-XX

### Added
- Map layer options: Street Map, Satellite, Satellite + Labels, Terrain, Dark
- Layer preference saved to localStorage
- Popup offset to prevent covering path line

### Fixed
- Popup positioning to not cover map markers/path

## [0.7.2] - 2025-01-XX

### Fixed
- "From" section now shows rich location info (business name + street address)
- Previous location lookup uses same place name system as current location

## [0.7.1] - 2025-01-XX

### Added
- Enhanced popup with duration at location
- Previous stable location with distance
- Contextual timestamp and duration formatting
- OpenStreetMap Nominatim for reverse geocoding
- Overpass API for nearby POI lookup
- Caching API results in localStorage

### Fixed
- Last location timestamp now uses current poll time (not device's last_updated)
- Config interval changes now sync to device preferences on startup

## [0.7.0] - 2025-01-XX

### Added
- Device management UI with clickable device cards
- +/- buttons for tracking (no dropdown needed)
- Persistent device preferences (survives restarts)
- Dynamic polling based on tracked devices
- Per-device interval configuration via UI

### Changed
- Device selection from dropdown to card-based UI
- Tracking preferences stored in `/data/tracked_devices.json`

## [0.6.0] - 2025-01-XX

### Added
- Time navigation slider with play button
- All markers visible on map
- Current marker highlighting
- Point counter display

### Fixed
- Time navigation now works with multiple data points

## [0.5.0] - 2025-01-XX

### Fixed
- Zone detection now correctly shows known zones (not "unknown")
- Fixed radius parsing (handles "100m" string format)
- Added detailed debug logging for zone detection

## [0.4.0] - 2025-01-XX

### Fixed
- InfluxDB field type conflict (accuracy as float)
- Device loading fallback to InfluxDB if HA API fails
- Web UI now loads devices correctly

## [0.3.0] - 2025-01-XX

### Added
- Web UI accessible via Ingress
- Basic HTML interface with map
- Device selection dropdown
- Location history visualization

### Fixed
- 503 Service Unavailable error resolved
- Static file serving configured

## [0.2.0] - 2025-01-XX

### Fixed
- InfluxDB hostname corrected (underscore to hyphen)
- HA API token auto-detection from SUPERVISOR_TOKEN
- API endpoints corrected for zones and device trackers

## [0.1.0] - 2025-01-XX

### Added
- Initial release
- Automatic location tracking from iCloud device trackers
- Zone detection using Home Assistant zones
- InfluxDB storage for historical data
- REST API for location history queries
- Basic polling mechanism
- S6 overlay service structure

### Features
- Polls device_tracker entities at configurable intervals
- Detects when devices are in known zones vs unknown locations
- Stores location data with tags and fields in InfluxDB
- Provides REST API for web interface
- Docker-based add-on architecture

### Technical
- Python-based backend
- aiohttp API server
- InfluxDB 1.x and 2.x compatibility
- Home Assistant API integration
- Haversine formula for distance calculation
- S6 overlay for process management

---

## Upgrade Notes

### From v0.7.x to v0.8.0+
- Battery data is now tracked automatically
- UI has been completely redesigned (Apple-style)
- Device management moved to web UI

### From v0.6.x to v0.7.x+
- Device preferences format changed
- Old `devices` config format still supported for backward compatibility

### From v0.4.x to v0.5.x+
- Zone detection improved - existing data may show different zone assignments
- Check zone configurations if locations appear incorrectly

### From v0.2.x to v0.3.x+
- Web UI now available via Ingress
- No need for Lovelace card (web UI is standalone)

---

For detailed feature descriptions, see [README.md](README.md).
