# Find My Location History - Design Specification v5

## Overview

Enhanced sidebar UI with person/device grouping, sensor status icons, and Phase 1 analytics features. All following Apple design principles.

**File to modify:** `find_my_history_addon/www/index.html`

---

## Layout Architecture

```
┌──────────────────────────┬─────────────────────────────────────┐
│  SIDEBAR (320px)         │                                     │
│                          │                                     │
│  Location History        │                                     │
│  ─────────────────────   │                                     │
│                          │           MAP AREA                   │
│  👤 User            │                                     │
│  ┌──────────────────┐     │    ● iPhone (primary)               │
│  │ ≡ iPhone  ✕     │     │    ● Apple Watch                   │
│  │   🔋⚡ 📍 🎯 📡  │     │                                     │
│  └──────────────────┘     │    (Auto-focused on iPhone)        │
│  ┌──────────────────┐     │                                     │
│  │   Apple Watch ✕   │     │  ┌─────────────────────────────┐  │
│  │   🔋 📍 🎯        │     │  │ ▶ ════●════ Today 13:48    │  │
│  └──────────────────┘     │  └─────────────────────────────┘  │
│                          │  □ Heatmap    [Map|Satellite]        │
│  👤 User 2               │                                     │
│  ┌──────────────────┐     │                                     │
│  │ ≡ iPad     ✕     │     │                                     │
│  └──────────────────┘     │                                     │
│                          │                                     │
│  + Add Person            │                                     │
│  ─────────────────────   │                                     │
│                          │                                     │
│  DEVICE DETAILS           │                                     │
│  (iPhone selected)        │                                     │
│                          │                                     │
│  📍 Caffeine Vilnius      │                                     │
│     Gedimino pr. 9        │                                     │
│                          │                                     │
│  🕐 Today, 13:48          │                                     │
│  ⏱️ Here for 6 min       │                                     │
│                          │                                     │
│  ← From: Home 749m        │                                     │
│                          │                                     │
│  🔋 33% ████░░░░░░ ⚡     │                                     │
│                          │                                     │
│  📊 STATS                 │                                     │
│  ─────────────────────    │                                     │
│  Most visited: Home       │                                     │
│  (12 visits, 45h total)   │                                     │
│                          │                                     │
│  Last updated: 1 min ago  │                                     │
│  [↻ Update Now]           │                                     │
└──────────────────────────┴─────────────────────────────────────┘
```

---

## Component 1: Person/Device Grouping

### Grouping Logic

```javascript
// Group devices by iCloud account (from HA entity attributes)
function groupDevicesByPerson(devices) {
    const groups = {};
    
    devices.forEach(device => {
        // Try to get iCloud account from attributes
        const account = device.attributes?.icloud_account || 
                       device.attributes?.account ||
                       extractPersonFromName(device.name);
        
        if (!groups[account]) {
            groups[account] = {
                name: account,
                devices: [],
                primaryDevice: null
            };
        }
        
        groups[account].devices.push(device);
    });
    
    // Determine primary device for each person
    Object.values(groups).forEach(group => {
        group.primaryDevice = findMostRecentlyMovedDevice(group.devices);
    });
    
    return Object.values(groups);
}

// Fallback: extract person name from device name
function extractPersonFromName(deviceName) {
    // "User's iPhone" → "User"
    const match = deviceName.match(/^(.+?)(?:'s|')\s/);
    return match ? match[1] : 'Unknown';
}

// Find most recently moved device
function findMostRecentlyMovedDevice(devices) {
    if (devices.length === 1) return devices[0];
    
    // Get recent location data for all devices
    const deviceScores = devices.map(device => {
        const recentLocations = getRecentLocations(device.entity_id, 30); // last 30 min
        if (!recentLocations || recentLocations.length < 2) {
            return { device, score: 0 };
        }
        
        // Calculate score: recent change + distance traveled
        const timeDiff = new Date(recentLocations[0].time) - 
                        new Date(recentLocations[recentLocations.length - 1].time);
        const distance = calculateTotalDistance(recentLocations);
        
        // Score: more recent = higher, more distance = higher
        const recencyScore = Math.max(0, 30 - (timeDiff / 60000)); // minutes ago
        const distanceScore = distance / 1000; // km
        
        return {
            device,
            score: recencyScore * 0.6 + distanceScore * 0.4
        };
    });
    
    // Return device with highest score
    deviceScores.sort((a, b) => b.score - a.score);
    return deviceScores[0].device;
}
```

### HTML Structure

```html
<div class="persons-list" id="persons-list">
    <!-- Person Group -->
    <div class="person-group" data-person="User">
        <div class="person-header" onclick="togglePersonGroup('User')">
            <span class="person-icon">👤</span>
            <span class="person-name">User</span>
            <span class="person-device-count">2 devices</span>
            <span class="person-toggle">▼</span>
        </div>
        
        <div class="person-devices">
            <!-- Primary device (most recently moved) -->
            <div class="device-chip selected primary" 
                 data-device-id="device_tracker.users_iphone"
                 data-person="User">
                <span class="drag-handle">≡</span>
                <span class="device-name">iPhone</span>
                <div class="device-sensors">
                    <span class="sensor-icon" title="Battery: 33%, Charging">🔋⚡</span>
                    <span class="sensor-icon" title="Distance: 2.4 km">📍</span>
                    <span class="sensor-icon" title="Focus: On">🎯</span>
                    <span class="sensor-icon" title="Connection: Wi-Fi">📡</span>
                    <span class="sensor-icon" title="Activity: Walking">🚶</span>
                </div>
                <button class="remove-btn">✕</button>
            </div>
            
            <!-- Secondary device -->
            <div class="device-chip" 
                 data-device-id="device_tracker.users_apple_watch"
                 data-person="User">
                <span class="drag-handle">≡</span>
                <span class="device-name">Apple Watch</span>
                <div class="device-sensors">
                    <span class="sensor-icon" title="Battery: 45%">🔋</span>
                    <span class="sensor-icon" title="Distance: 1.2 km">📍</span>
                    <span class="sensor-icon" title="Focus: On">🎯</span>
                </div>
                <button class="remove-btn">✕</button>
            </div>
        </div>
    </div>
    
    <!-- Standalone device (no person group) -->
    <div class="device-chip standalone" data-device-id="device_tracker.ipad">
        <span class="drag-handle">≡</span>
        <span class="device-name">iPad</span>
        <div class="device-sensors">
            <span class="sensor-icon" title="Battery: 78%">🔋</span>
        </div>
        <button class="remove-btn">✕</button>
    </div>
</div>
```

### CSS

```css
.person-group {
    margin-bottom: var(--spacing-md);
}

.person-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    cursor: pointer;
    border-radius: var(--radius-md);
    transition: background 0.2s;
}

.person-header:hover {
    background: var(--bg-tertiary);
}

.person-icon {
    font-size: 18px;
}

.person-name {
    flex: 1;
    font-weight: 600;
    font-size: var(--font-size-subhead);
}

.person-device-count {
    font-size: var(--font-size-caption);
    color: var(--text-secondary);
}

.person-toggle {
    font-size: 12px;
    color: var(--text-tertiary);
    transition: transform 0.2s;
}

.person-group.collapsed .person-toggle {
    transform: rotate(-90deg);
}

.person-devices {
    padding-left: var(--spacing-lg);
    margin-top: var(--spacing-xs);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
}

.person-group.collapsed .person-devices {
    display: none;
}

/* Device chip with sensors */
.device-chip {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    background: var(--bg-tertiary);
    border-radius: var(--radius-md);
    cursor: grab;
    transition: all 0.2s ease;
    border: 2px solid transparent;
}

.device-chip.primary {
    border-color: var(--apple-green);
    background: rgba(52, 199, 89, 0.1);
}

.device-chip.selected {
    border-color: var(--apple-blue);
    background: rgba(0, 122, 255, 0.15);
}

.device-sensors {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-left: auto;
    margin-right: var(--spacing-xs);
}

.sensor-icon {
    font-size: 14px;
    opacity: 0.8;
    cursor: help;
    transition: opacity 0.2s;
}

.sensor-icon:hover {
    opacity: 1;
    transform: scale(1.2);
}

/* Sensor icon colors */
.sensor-icon[title*="Charging"] {
    color: var(--apple-green);
}

.sensor-icon[title*="Battery"][title*="%"] {
    /* Extract battery % and color code */
}

.sensor-icon[title*="Focus: On"] {
    color: var(--apple-yellow);
}
```

---

## Component 2: Sensor Icons Integration

### Sensor Data Fetching

```javascript
// Fetch sensor data for a device
async function fetchDeviceSensors(deviceId) {
    const sensors = {
        battery_level: null,
        battery_state: null,
        distance: null,
        focus: null,
        connection_type: null,
        activity: null
    };
    
    // Map device_tracker to sensor entities
    const baseId = deviceId.replace('device_tracker.', '');
    
    const sensorMappings = {
        battery_level: `sensor.${baseId}_battery_level`,
        battery_state: `sensor.${baseId}_battery_state`,
        distance: `sensor.${baseId}_distance`,
        focus: `binary_sensor.${baseId}_focus`,
        connection_type: `sensor.${baseId}_connection_type`,
        activity: `sensor.${baseId}_activity`
    };
    
    // Fetch all sensors in parallel
    const promises = Object.entries(sensorMappings).map(async ([key, entityId]) => {
        try {
            const response = await fetch(`./api/states/${entityId}`);
            const data = await response.json();
            return { key, value: data?.state, attributes: data?.attributes };
        } catch (error) {
            return { key, value: null };
        }
    });
    
    const results = await Promise.all(promises);
    results.forEach(({ key, value, attributes }) => {
        sensors[key] = { value, attributes };
    });
    
    return sensors;
}

// Render sensor icons
function renderSensorIcons(sensors) {
    const icons = [];
    
    // Battery
    if (sensors.battery_level?.value !== null) {
        const level = parseInt(sensors.battery_level.value);
        const isCharging = sensors.battery_state?.value === 'charging';
        icons.push({
            icon: '🔋',
            title: `Battery: ${level}%${isCharging ? ', Charging' : ''}`,
            color: getBatteryColor(level, isCharging),
            charging: isCharging
        });
    }
    
    // Distance
    if (sensors.distance?.value !== null) {
        const distance = parseFloat(sensors.distance.value);
        icons.push({
            icon: '📍',
            title: `Distance: ${formatDistance(distance)}`,
            color: null
        });
    }
    
    // Focus
    if (sensors.focus?.value !== null) {
        const isOn = sensors.focus.value === 'on';
        icons.push({
            icon: '🎯',
            title: `Focus: ${isOn ? 'On' : 'Off'}`,
            color: isOn ? 'var(--apple-yellow)' : null
        });
    }
    
    // Connection
    if (sensors.connection_type?.value !== null) {
        const type = sensors.connection_type.value;
        icons.push({
            icon: type === 'wifi' ? '📡' : '📶',
            title: `Connection: ${type}`,
            color: null
        });
    }
    
    // Activity
    if (sensors.activity?.value !== null) {
        const activity = sensors.activity.value.toLowerCase();
        const activityIcons = {
            walking: '🚶',
            running: '🏃',
            cycling: '🚴',
            driving: '🚗',
            stationary: '⏸'
        };
        icons.push({
            icon: activityIcons[activity] || '📍',
            title: `Activity: ${sensors.activity.value}`,
            color: null
        });
    }
    
    return icons;
}
```

### Sensor Icon HTML

```html
<div class="device-sensors">
    <span class="sensor-icon" 
          style="color: var(--apple-green);"
          title="Battery: 33%, Charging">
        🔋⚡
    </span>
    <span class="sensor-icon" title="Distance: 2.4 km">📍</span>
    <span class="sensor-icon" 
          style="color: var(--apple-yellow);"
          title="Focus: On">
        🎯
    </span>
    <span class="sensor-icon" title="Connection: Wi-Fi">📡</span>
    <span class="sensor-icon" title="Activity: Walking">🚶</span>
</div>
```

---

## Component 3: Multi-Device Map Display

### Map Rendering Logic

```javascript
// When person is selected, show all their devices
function renderPersonDevicesOnMap(personName) {
    const person = persons.find(p => p.name === personName);
    if (!person) return;
    
    // Clear existing markers
    clearAllMarkers();
    
    // Render all devices for this person
    person.devices.forEach(device => {
        const locations = getDeviceLocations(device.entity_id);
        if (locations.length === 0) return;
        
        const isPrimary = device.entity_id === person.primaryDevice.entity_id;
        
        // Create path
        if (locations.length > 1) {
            const path = L.polyline(
                locations.map(l => [l.latitude, l.longitude]),
                {
                    color: isPrimary ? '#007AFF' : '#8E8E93',
                    weight: isPrimary ? 3 : 2,
                    opacity: isPrimary ? 0.8 : 0.5
                }
            ).addTo(map);
        }
        
        // Create marker
        const latest = locations[0];
        const marker = L.marker(
            [latest.latitude, latest.longitude],
            {
                icon: createDeviceIcon(device, isPrimary)
            }
        ).addTo(map);
        
        // Minimal popup
        marker.bindPopup(`
            <div class="findmy-popup">
                <div class="popup-title">${device.name}</div>
                <div class="popup-subtitle">${formatRelativeTime(new Date(latest.time))}</div>
            </div>
        `);
        
        // Click to select device
        marker.on('click', () => {
            selectDevice(device.entity_id);
        });
    });
    
    // Auto-focus on primary device
    if (person.primaryDevice) {
        const primaryLocations = getDeviceLocations(person.primaryDevice.entity_id);
        if (primaryLocations.length > 0) {
            const bounds = primaryLocations.map(l => [l.latitude, l.longitude]);
            map.fitBounds(bounds, { padding: [50, 50] });
        }
    }
}

// Create device icon
function createDeviceIcon(device, isPrimary) {
    const color = isPrimary ? '#007AFF' : '#8E8E93';
    const size = isPrimary ? 24 : 18;
    
    return L.divIcon({
        className: 'device-marker',
        html: `
            <div style="
                width: ${size}px;
                height: ${size}px;
                background: ${color};
                border-radius: 50%;
                border: 3px solid white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            "></div>
        `,
        iconSize: [size, size],
        iconAnchor: [size/2, size/2]
    });
}
```

---

## Component 4: Phase 1 Analytics Features

### 4.1 Visit Frequency (Most Visited Places)

**Effort:** Low | **Battery Impact:** None

```javascript
// Calculate most visited places
function calculateVisitFrequency(deviceId, timeRange) {
    const locations = getDeviceLocations(deviceId, timeRange);
    
    // Group by location cluster (100m radius)
    const places = {};
    
    locations.forEach(loc => {
        const key = getLocationClusterKey(loc.latitude, loc.longitude, 100);
        
        if (!places[key]) {
            places[key] = {
                latitude: loc.latitude,
                longitude: loc.longitude,
                name: loc.zone_name || 'Unknown',
                visits: 0,
                totalTime: 0,
                firstSeen: loc.time,
                lastSeen: loc.time
            };
        }
        
        places[key].visits++;
        places[key].lastSeen = loc.time;
    });
    
    // Calculate total time spent at each place
    Object.values(places).forEach(place => {
        const placeLocations = locations.filter(loc => 
            getLocationClusterKey(loc.latitude, loc.longitude, 100) === 
            getLocationClusterKey(place.latitude, place.longitude, 100)
        );
        
        place.totalTime = calculateTimeSpent(placeLocations);
    });
    
    // Sort by visits, then by total time
    return Object.values(places)
        .sort((a, b) => {
            if (b.visits !== a.visits) return b.visits - a.visits;
            return b.totalTime - a.totalTime;
        });
}

// Display in sidebar
function renderVisitFrequency(deviceId) {
    const places = calculateVisitFrequency(deviceId, '30d');
    const topPlaces = places.slice(0, 5);
    
    const html = `
        <div class="stats-section">
            <h3 class="stats-title">Most Visited</h3>
            ${topPlaces.map(place => `
                <div class="stat-item">
                    <span class="stat-place">${place.name}</span>
                    <span class="stat-meta">
                        ${place.visits} visits, ${formatDuration(place.totalTime)}
                    </span>
                </div>
            `).join('')}
        </div>
    `;
    
    document.getElementById('device-details').insertAdjacentHTML('beforeend', html);
}
```

### 4.2 Trip Detection

**Effort:** Medium | **Battery Impact:** None

```javascript
// Detect trips (movement between stable locations)
function detectTrips(deviceId, timeRange) {
    const locations = getDeviceLocations(deviceId, timeRange);
    const trips = [];
    let currentTrip = null;
    
    for (let i = 1; i < locations.length; i++) {
        const prev = locations[i - 1];
        const curr = locations[i];
        const distance = getDistance(prev, curr);
        const timeDiff = new Date(curr.time) - new Date(prev.time);
        
        // Trip starts: moved > 500m in < 2 hours
        if (distance > 500 && timeDiff < 2 * 60 * 60 * 1000) {
            if (!currentTrip) {
                currentTrip = {
                    start: prev,
                    end: curr,
                    distance: distance,
                    duration: timeDiff
                };
            } else {
                currentTrip.end = curr;
                currentTrip.distance += distance;
                currentTrip.duration += timeDiff;
            }
        } else {
            // Trip ends: stopped moving
            if (currentTrip && currentTrip.distance > 1000) {
                trips.push(currentTrip);
            }
            currentTrip = null;
        }
    }
    
    // Add final trip if exists
    if (currentTrip && currentTrip.distance > 1000) {
        trips.push(currentTrip);
    }
    
    return trips.map(trip => ({
        ...trip,
        startName: trip.start.zone_name || 'Unknown',
        endName: trip.end.zone_name || 'Unknown',
        avgSpeed: (trip.distance / trip.duration) * 3.6 // km/h
    }));
}
```

### 4.3 Movement Speed

**Effort:** Low | **Battery Impact:** None

```javascript
// Calculate speed between points
function calculateSpeed(loc1, loc2) {
    const distance = getDistance(loc1, loc2); // meters
    const time = (new Date(loc2.time) - new Date(loc1.time)) / 1000; // seconds
    if (time === 0) return 0;
    return (distance / time) * 3.6; // km/h
}

// Display in popup
function addSpeedToPopup(location, previousLocation) {
    if (!previousLocation) return '';
    
    const speed = calculateSpeed(previousLocation, location);
    let speedLabel = 'Stationary';
    
    if (speed > 80) speedLabel = 'Driving';
    else if (speed > 20) speedLabel = 'Cycling';
    else if (speed > 5) speedLabel = 'Walking';
    
    return `
        <div class="speed-indicator">
            🚗 ${speedLabel} (${speed.toFixed(1)} km/h)
        </div>
    `;
}
```

---

## Component 5: Timeline Navigation with Previous/Next Location

### Problem
Currently, "From:" shows the first location in history or a stable location from 30+ minutes ago. When navigating through the timeline, users need to see the actual previous and next location points relative to the currently selected point.

### Solution
Show previous/next locations based on the current timeline position, updating dynamically as user navigates.

### Timeline Navigation Logic

```javascript
let currentLocationIndex = 0; // Index in locations array
let locations = []; // Sorted by time, newest first

// Get previous and next locations for current index
function getAdjacentLocations(index) {
    const previous = index < locations.length - 1 ? locations[index + 1] : null;
    const current = locations[index];
    const next = index > 0 ? locations[index - 1] : null;
    
    return { previous, current, next };
}

// Update sidebar when timeline position changes
function updateLocationDetails(index) {
    const { previous, current, next } = getAdjacentLocations(index);
    
    // Update current location display
    updateCurrentLocationDisplay(current);
    
    // Update previous location (if exists)
    if (previous) {
        const distance = getDistance(previous, current);
        const placeName = previous.zone_name || 
                         await getNearbyPlaceName(previous.latitude, previous.longitude) ||
                         `${previous.latitude.toFixed(4)}, ${previous.longitude.toFixed(4)}`;
        
        updatePreviousLocationDisplay(placeName, distance);
    } else {
        hidePreviousLocation();
    }
    
    // Update next location (if exists)
    if (next) {
        const distance = getDistance(current, next);
        const placeName = next.zone_name || 
                         await getNearbyPlaceName(next.latitude, next.longitude) ||
                         `${next.latitude.toFixed(4)}, ${next.longitude.toFixed(4)}`;
        
        updateNextLocationDisplay(placeName, distance);
    } else {
        hideNextLocation();
    }
}

// Time slider change handler
function onTimeSliderChange(value) {
    // Convert slider value (0-100) to index
    const index = Math.floor((value / 100) * Math.max(locations.length - 1, 0));
    currentLocationIndex = index;
    
    // Update map marker
    updateMapMarker(locations[index]);
    
    // Update sidebar with previous/next
    updateLocationDetails(index);
}

// Navigation buttons
function navigateToPrevious() {
    if (currentLocationIndex < locations.length - 1) {
        currentLocationIndex++;
        const sliderValue = (currentLocationIndex / Math.max(locations.length - 1, 1)) * 100;
        document.getElementById('time-slider').value = sliderValue;
        onTimeSliderChange(sliderValue);
    }
}

function navigateToNext() {
    if (currentLocationIndex > 0) {
        currentLocationIndex--;
        const sliderValue = (currentLocationIndex / Math.max(locations.length - 1, 1)) * 100;
        document.getElementById('time-slider').value = sliderValue;
        onTimeSliderChange(sliderValue);
    }
}
```

### Updated HTML Structure

```html
<!-- Origin Section - Now shows Previous and Next -->
<div class="detail-section">
    <!-- Previous Location -->
    <div class="location-nav previous" id="previous-location" style="display: none;">
        <button class="nav-button prev" onclick="navigateToPrevious()" title="Go to previous location">
            ◀
        </button>
        <div class="location-nav-info">
            <div class="location-nav-label">← From</div>
            <div class="location-nav-place" id="previous-place">Home</div>
            <div class="location-nav-distance" id="previous-distance">749 m away</div>
        </div>
    </div>
    
    <!-- Next Location -->
    <div class="location-nav next" id="next-location" style="display: none;">
        <div class="location-nav-info">
            <div class="location-nav-label">To →</div>
            <div class="location-nav-place" id="next-place">Work</div>
            <div class="location-nav-distance" id="next-distance">2.1 km away</div>
        </div>
        <button class="nav-button next" onclick="navigateToNext()" title="Go to next location">
            ▶
        </button>
    </div>
</div>
```

### CSS

```css
.location-nav {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) 0;
}

.location-nav.previous {
    border-bottom: 1px solid var(--apple-gray4);
    padding-bottom: var(--spacing-md);
    margin-bottom: var(--spacing-sm);
}

.location-nav.next {
    padding-top: var(--spacing-md);
    margin-top: var(--spacing-sm);
}

.nav-button {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: var(--bg-tertiary);
    border: 1px solid var(--apple-gray4);
    color: var(--text-primary);
    font-size: 14px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    flex-shrink: 0;
}

.nav-button:hover {
    background: var(--apple-blue);
    border-color: var(--apple-blue);
    color: white;
}

.nav-button:disabled {
    opacity: 0.3;
    cursor: not-allowed;
}

.location-nav-info {
    flex: 1;
}

.location-nav-label {
    font-size: var(--font-size-caption);
    color: var(--text-secondary);
    margin-bottom: 2px;
}

.location-nav-place {
    font-size: var(--font-size-subhead);
    font-weight: 500;
    color: var(--text-primary);
}

.location-nav-distance {
    font-size: var(--font-size-caption2);
    color: var(--text-tertiary);
    margin-top: 2px;
}
```

### Update Functions

```javascript
function updatePreviousLocationDisplay(placeName, distance) {
    const section = document.getElementById('previous-location');
    document.getElementById('previous-place').textContent = placeName;
    document.getElementById('previous-distance').textContent = formatDistance(distance);
    section.style.display = 'flex';
    
    // Enable/disable button
    const button = section.querySelector('.nav-button');
    button.disabled = currentLocationIndex >= locations.length - 1;
}

function updateNextLocationDisplay(placeName, distance) {
    const section = document.getElementById('next-location');
    document.getElementById('next-place').textContent = placeName;
    document.getElementById('next-distance').textContent = formatDistance(distance);
    section.style.display = 'flex';
    
    // Enable/disable button
    const button = section.querySelector('.nav-button');
    button.disabled = currentLocationIndex <= 0;
}

function hidePreviousLocation() {
    document.getElementById('previous-location').style.display = 'none';
}

function hideNextLocation() {
    document.getElementById('next-location').style.display = 'none';
}
```

### Time Navigation Controls Enhancement

```html
<div class="time-nav">
    <button class="time-nav-btn" id="prev-btn" onclick="navigateToPrevious()">
        <span class="icon">◀</span>
    </button>
    <button class="time-nav-btn" id="play-btn" onclick="togglePlay()">
        <span class="icon">▶</span>
    </button>
    <div class="time-slider-wrapper">
        <input type="range" id="time-slider" min="0" max="100" value="100">
        <div class="time-markers">
            <span class="marker start">00:00</span>
            <span class="marker end">23:59</span>
        </div>
    </div>
    <div class="time-display">
        <span class="time-current">Today, 13:48</span>
        <span class="time-points">42 pts</span>
    </div>
    <button class="time-nav-btn" id="next-btn" onclick="navigateToNext()">
        <span class="icon">▶</span>
    </button>
</div>
```

### Visual Example

```
┌─────────────────────────────────────┐
│  ← From: Home                       │
│     749 m away          [◀]        │
│  ─────────────────────────────────   │
│  📍 Caffeine Vilnius                │
│     Gedimino pr. 9                  │
│  ─────────────────────────────────   │
│  To →: Work                         │
│     2.1 km away          [▶]        │
└─────────────────────────────────────┘
```

---

## Component 6: Enhanced Sidebar Stats Section

### HTML Structure

```html
<section class="details-section" id="device-details">
    <!-- Location Info -->
    <div class="detail-section">
        <div class="location-info">
            <div class="place-name">📍 Caffeine Vilnius</div>
            <div class="place-address">Gedimino pr. 9</div>
        </div>
    </div>
    
    <div class="sidebar-divider"></div>
    
    <!-- Timing -->
    <div class="detail-section">
        <div class="timing-row">
            <span class="timing-icon">🕐</span>
            <span class="timing-value">Today, 13:48</span>
        </div>
        <div class="timing-row">
            <span class="timing-icon">⏱️</span>
            <span class="timing-value">Here for 6 min</span>
        </div>
    </div>
    
    <div class="sidebar-divider"></div>
    
    <!-- Origin -->
    <div class="detail-section">
        <div class="origin-row">
            <span class="origin-arrow">←</span>
            <span class="origin-text">From: Home</span>
            <span class="origin-distance">749 m away</span>
        </div>
    </div>
    
    <div class="sidebar-divider"></div>
    
    <!-- Battery -->
    <div class="detail-section">
        <div class="battery-row">
            <span class="battery-icon">🔋</span>
            <div class="battery-info">
                <div class="battery-percentage">33%</div>
                <div class="battery-bar">
                    <div class="battery-fill" style="width: 33%; background: var(--apple-yellow);"></div>
                </div>
            </div>
            <span class="charging-indicator">⚡</span>
        </div>
    </div>
    
    <div class="sidebar-divider"></div>
    
    <!-- Phase 1 Stats -->
    <div class="stats-section">
        <h3 class="stats-title">📊 Statistics</h3>
        
        <div class="stat-item">
            <div class="stat-label">Most Visited</div>
            <div class="stat-value">Home</div>
            <div class="stat-meta">12 visits, 45h total</div>
        </div>
        
        <div class="stat-item">
            <div class="stat-label">Trips Today</div>
            <div class="stat-value">3</div>
            <div class="stat-meta">12.4 km total</div>
        </div>
        
        <div class="stat-item">
            <div class="stat-label">Current Speed</div>
            <div class="stat-value">Walking</div>
            <div class="stat-meta">4.2 km/h</div>
        </div>
    </div>
    
    <div class="sidebar-divider"></div>
    
    <!-- Actions -->
    <div class="detail-section">
        <div class="last-updated">Last updated: 1 min ago</div>
        <button class="update-button" onclick="updateDeviceLocation()">
            <span class="update-icon">↻</span>
            Update Now
        </button>
    </div>
</section>
```

### CSS

```css
.stats-section {
    margin: var(--spacing-md) 0;
}

.stats-title {
    font-size: var(--font-size-subhead);
    font-weight: 600;
    margin-bottom: var(--spacing-sm);
    color: var(--text-primary);
}

.stat-item {
    padding: var(--spacing-sm) 0;
    border-bottom: 1px solid var(--apple-gray4);
}

.stat-item:last-child {
    border-bottom: none;
}

.stat-label {
    font-size: var(--font-size-caption);
    color: var(--text-secondary);
    margin-bottom: 2px;
}

.stat-value {
    font-size: var(--font-size-subhead);
    font-weight: 600;
    color: var(--text-primary);
}

.stat-meta {
    font-size: var(--font-size-caption2);
    color: var(--text-tertiary);
    margin-top: 2px;
}
```

---

## API Enhancements

### New Endpoints

```python
# In api.py

@app.route('/api/devices/{device_id}/sensors', methods=['GET'])
async def get_device_sensors(device_id: str):
    """Get all sensor data for a device."""
    # Fetch sensor entities from HA
    # Return battery, distance, focus, connection, activity

@app.route('/api/persons', methods=['GET'])
async def get_persons():
    """Get all persons with their devices grouped."""
    # Group devices by iCloud account
    # Return list of persons with device lists

@app.route('/api/devices/{device_id}/stats', methods=['GET'])
async def get_device_stats(device_id: str, time_range: str = '30d'):
    """Get analytics stats for a device."""
    # Calculate visit frequency, trips, etc.
    # Return JSON with stats
```

---

## Acceptance Criteria

1. Devices grouped by person (iCloud account detection)
2. Person groups collapsible/expandable
3. Primary device (most recently moved) highlighted in green
4. Sensor icons displayed on device chips (battery, distance, focus, connection, activity)
5. Selecting person shows all their devices on map
6. Auto-focus on primary device when multiple devices shown
7. Timeline navigation shows actual previous location (not first in history)
8. Timeline navigation shows next location (if exists)
9. Previous/Next buttons navigate through timeline points
10. Previous/Next location updates dynamically as user moves slider
11. Visit frequency stats displayed in sidebar
12. Trip detection working (shows trips in stats)
13. Movement speed calculated and displayed
14. All following Apple design principles
15. Zero battery impact (all features use existing data)

---

## Implementation Phases

### Phase 1A: Person/Device Grouping (Week 1)
- [ ] Group devices by iCloud account
- [ ] Person group UI with collapse/expand
- [ ] Primary device detection (recent movement + distance)
- [ ] Multi-device map rendering

### Phase 1B: Sensor Icons (Week 1)
- [ ] Fetch sensor data from HA
- [ ] Render sensor icons on device chips
- [ ] Color coding for battery/charging/focus
- [ ] Tooltips with sensor values

### Phase 1C: Timeline Navigation Fix (Week 2)
- [ ] Previous/next location logic based on current index
- [ ] Navigation buttons (◀ ▶) in sidebar
- [ ] Dynamic update on slider change
- [ ] Show/hide previous/next based on availability

### Phase 1D: Analytics (Week 2)
- [ ] Visit frequency calculation
- [ ] Trip detection algorithm
- [ ] Movement speed calculation
- [ ] Stats display in sidebar

### Phase 1E: Polish (Week 2)
- [ ] Apple design refinements
- [ ] Animations and transitions
- [ ] Responsive mobile layout
- [ ] Performance optimization
