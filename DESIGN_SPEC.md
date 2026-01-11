# Find My Location History - UI Enhancement Specification

## Project Context

**File to modify:** `find_my_history_addon/www/index.html`

This is a Home Assistant addon that displays device location history on a map. The current UI shows all devices (tracked and untracked) as equal-sized cards in a grid. See the existing implementation for current styling conventions (dark theme, CSS variables, Leaflet.js for maps).

---

## Feature 1: Tracked Devices as Buttons

**Current behavior:** All devices display as cards in a uniform grid with +/- buttons to toggle tracking.

**Desired behavior:** Tracked devices should appear as prominent, pill-shaped buttons in a horizontal row at the top.

**Requirements:**
- Display tracked devices as horizontal pill/chip buttons (not cards)
- Show device name and current state (home/not_home) inside the button
- Clicking a button selects that device for viewing on the map
- Selected device should have distinct visual styling (e.g., blue border/glow)
- Small "X" or "−" icon on each button to remove from tracking
- Buttons should wrap to multiple rows if many devices are tracked
- Use existing color scheme: green accent for "home" state, yellow/amber for "not_home"

**Visual example:**
```
[ m1 (home) ✕ ]  [ Viktorija's iPhone (not_home) ✕ ]
```

---

## Feature 2: Collapsible Non-Tracked Devices Section

**Current behavior:** All 20 devices show in the grid, making the UI cluttered.

**Desired behavior:** Non-tracked devices should be collapsed by default to save space.

**Requirements:**
- Create a collapsible section below the tracked device buttons
- Header shows: "▶ 18 more devices" (or similar count)
- Clicking the header expands/collapses the section
- When expanded, show the grid of non-tracked device cards (current card design is fine)
- Each non-tracked card has a "+" button to add to tracking
- When a device is added to tracking, it moves to the tracked buttons row
- Default state: collapsed
- Use CSS transitions for smooth expand/collapse animation
- Store collapse state in localStorage (optional)

**Visual structure:**

```
+------------------------------------------+
| [Tracked Device 1] [Tracked Device 2]    |  <- Buttons
+------------------------------------------+
| ▶ 18 more devices                        |  <- Collapsed header
+------------------------------------------+
```

When expanded:

```
+------------------------------------------+
| [Tracked Device 1] [Tracked Device 2]    |
+------------------------------------------+
| ▼ 18 more devices                        |
|  +--------+  +--------+  +--------+      |
|  | Dev 3  |  | Dev 4  |  | Dev 5  |      |
|  |  [+]   |  |  [+]   |  |  [+]   |      |
|  +--------+  +--------+  +--------+      |
|  ... more cards ...                      |
+------------------------------------------+
```

---

## Feature 3: Location Heatmap Layer

**Purpose:** Visualize time spent at different locations using a heatmap overlay on the map.

**Requirements:**
- Add Leaflet.heat library: `https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js`
- Create a heatmap layer showing location density/time spent
- **Hidden by default** - user must toggle it on
- **Scoped to selected device only** (not all devices)

**Heatmap intensity calculation:**
- Group nearby location points (within ~50 meters) as the same "spot"
- Calculate weight based on time spent:
  - If consecutive points are at same location, sum the time gaps
  - More time at a location = higher heat intensity
- Alternative simpler approach: just use point density (more data points = more heat)

**UI for toggle:**
- Add a checkbox or toggle button near the map: `☐ Show Heatmap`
- When enabled, overlay the heatmap layer on the map
- Heatmap should not obscure the path line or markers significantly (use appropriate opacity)

**Heatmap styling:**
- Radius: ~25-30 pixels
- Blur: ~15-20 pixels  
- Gradient: blue (cold/low) → green → yellow → red (hot/high)
- Max opacity: 0.6-0.7

**Implementation hint using Leaflet.heat:**

```javascript
// After loading locations data:
const heatData = locations.map(loc => [
    loc.latitude, 
    loc.longitude, 
    intensity  // calculated weight
]);

const heatLayer = L.heatLayer(heatData, {
    radius: 25,
    blur: 15,
    maxZoom: 17,
    gradient: {0.4: 'blue', 0.6: 'lime', 0.8: 'yellow', 1: 'red'}
});

// Toggle on/off based on checkbox
```

---

## Feature 4: Enhanced Location Popup with Duration and Previous Location

**Current behavior:** Popup shows device name, time, zone, and coordinates only.

**Desired behavior:** Show how long the device stayed at this location and where they came from (previous stable location).

### 4.1 Duration at Current Location

**Requirements:**
- Calculate time spent at the current location cluster
- A "location cluster" = all points within **100 meters radius** of the selected point
- Display duration in the popup: "Duration: 2h 15m" or "Duration: 45m"
- Look at consecutive points in the same cluster and sum the time gaps

**Algorithm:**
```
1. For the selected location point, find all consecutive points within 100m radius
2. First point in cluster = arrival time
3. Last point in cluster = departure time (or "now" if still there)
4. Duration = departure - arrival
```

**Distance calculation (Haversine formula):**
```javascript
function getDistance(lat1, lon1, lat2, lon2) {
    const R = 6371000; // Earth radius in meters
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c; // Distance in meters
}
```

### 4.2 Previous Stable Location

**Purpose:** Show where the device was before arriving at the current location, filtering out transit (walking/driving).

**Definition of "stable location":**
- Device stayed in the same location cluster (100m radius) for **at least 30 minutes**

**Requirements:**
- Find the previous stable location before the current one
- Skip over transit points (locations where device was moving/passing through)
- Display in popup: "From: Home (1.2 km away)" or "From: 54.7123, 25.2456 (3.5 km)"
- If previous stable location is a known zone, show the zone name
- Show distance from previous stable location to current location

**Algorithm:**
```
1. Starting from current location, go backwards in time through location points
2. Skip points that are within the current location cluster (100m radius)
3. For each new cluster found, check if device stayed there for 30+ minutes
4. If yes -> this is the "previous stable location"
5. If no -> continue searching backwards
6. Calculate distance between previous stable location and current location
```

**Visual example - Enhanced Popup:**
```
+----------------------------------+
| Viktorija's iPhone           ✕  |
+----------------------------------+
| Time: 11/01/2026, 12:50:12       |
| Zone: Unknown                    |
| Coords: 54.71881, 25.30142       |
+----------------------------------+
| ⏱ Duration: 1h 23m               |
| ← From: Home (2.4 km away)       |
+----------------------------------+
```

**Edge cases:**
- If no previous stable location found: show "From: -" or hide the line
- If current location is the first in history: show "From: Start of tracking"
- If previous stable location has no zone: show coordinates instead

---

## Technical Notes

- The existing code uses vanilla JavaScript (no framework)
- Map is Leaflet.js with OpenStreetMap tiles
- API endpoints are relative (`./api/devices`, `./api/locations`)
- Existing layer groups: `pathLayer`, `allMarkersLayer`, `markerLayer`
- Add new layer: `heatLayer` for the heatmap
- Maintain dark theme consistency (#1c1c1c background, #2a2a2a cards, #e1e1e1 text)

---

## Acceptance Criteria

1. Tracked devices render as clickable pill buttons, not cards
2. Non-tracked devices are hidden in a collapsible section by default
3. Clicking expand reveals the grid of non-tracked devices
4. Adding a device to tracking moves it to the button row
5. Heatmap toggle exists and is OFF by default
6. Enabling heatmap shows time-weighted heat overlay for selected device
7. Location popup shows duration at current location (points within 100m radius)
8. Location popup shows previous stable location (stayed 30+ mins) with distance
9. All existing functionality (map, path, markers, playback) continues to work
