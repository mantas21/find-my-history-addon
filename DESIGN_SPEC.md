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
7. All existing functionality (map, path, markers, playback) continues to work
