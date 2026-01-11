# Find My Location History - Design Specification v4

## Overview

Complete UI redesign following Apple Find My design principles. Replace popup-heavy interface with a sidebar layout for better UX and consistent Apple ecosystem experience.

**File to modify:** `find_my_history_addon/www/index.html`

---

## Layout Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  Location History                                        [Settings] │
├──────────────────────────┬──────────────────────────────────────────┤
│                          │                                          │
│  ┌──────────────────┐    │                                          │
│  │ ≡ iPhone  ✕      │    │                                          │
│  └──────────────────┘    │                                          │
│  ┌──────────────────┐    │                                          │
│  │   iPad    ✕      │    │              MAP AREA                    │
│  └──────────────────┘    │                                          │
│                          │         (Full width, no popup)           │
│  + Add Device            │                                          │
│                          │              ● Device marker             │
│  ─────────────────────   │              (minimal, clickable)        │
│                          │                                          │
│  DEVICE DETAILS          │                                          │
│                          │                                          │
│  📍 Caffeine Vilnius     │                                          │
│     Gedimino pr. 9       │                                          │
│                          │                                          │
│  🕐 Today, 13:48         │  ┌─────────────────────────────────────┐ │
│  ⏱️ Here for 6 min       │  │ ◀ ══════════●══════ ▶  Today 13:48 │ │
│                          │  └─────────────────────────────────────┘ │
│  ← From: Home            │  □ Heatmap    ⊞ Satellite               │
│    749 m away            │                                          │
│                          ├──────────────────────────────────────────┤
│  🔋 33% ████░░░░░░       │                                          │
│                          │                                          │
│  Last updated: 1 min ago │                                          │
│  ┌──────────────────┐    │                                          │
│  │  ↻ Update Now    │    │                                          │
│  └──────────────────┘    │                                          │
│                          │                                          │
└──────────────────────────┴──────────────────────────────────────────┘
```

---

## Component 1: Sidebar (Left Panel)

### Structure

```html
<aside class="sidebar">
    <!-- Tracked Devices (Draggable) -->
    <section class="devices-section">
        <div class="devices-list" id="tracked-devices">
            <!-- Draggable device chips -->
        </div>
        <button class="add-device-btn">+ Add Device</button>
    </section>
    
    <div class="sidebar-divider"></div>
    
    <!-- Device Details -->
    <section class="details-section" id="device-details">
        <!-- Location, timing, battery, etc. -->
    </section>
</aside>
```

### Sidebar CSS

```css
.sidebar {
    width: 320px;
    min-width: 280px;
    max-width: 380px;
    height: 100vh;
    background: var(--bg-secondary);
    border-right: 1px solid var(--apple-gray4);
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    flex-shrink: 0;
}

.devices-section {
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--apple-gray4);
}

.devices-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.sidebar-divider {
    height: 1px;
    background: var(--apple-gray4);
}

.details-section {
    flex: 1;
    padding: var(--spacing-lg);
    overflow-y: auto;
}
```

---

## Component 2: Draggable Device Chips

### Features
- Drag handle (≡) on left side
- Device name in center
- Remove button (✕) on right
- First device in list = default selected on page load
- Reorder persisted to localStorage

### HTML Structure

```html
<div class="device-chip selected" draggable="true" data-device-id="device_tracker.iphone">
    <span class="drag-handle">≡</span>
    <span class="device-name">iPhone</span>
    <span class="device-state home"></span>
    <button class="remove-btn" title="Remove">✕</button>
</div>
```

### CSS

```css
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

.device-chip:active {
    cursor: grabbing;
}

.device-chip.selected {
    border-color: var(--apple-blue);
    background: rgba(0, 122, 255, 0.15);
}

.device-chip.dragging {
    opacity: 0.5;
    transform: scale(1.02);
}

.device-chip.drag-over {
    border-color: var(--apple-green);
}

.drag-handle {
    color: var(--text-tertiary);
    font-size: 14px;
    cursor: grab;
}

.device-name {
    flex: 1;
    font-weight: 500;
    font-size: var(--font-size-subhead);
}

.device-state {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--apple-gray);
}

.device-state.home {
    background: var(--apple-green);
}

.device-state.not_home {
    background: var(--apple-yellow);
}

.remove-btn {
    background: none;
    border: none;
    color: var(--text-tertiary);
    font-size: 14px;
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    opacity: 0;
    transition: opacity 0.2s;
}

.device-chip:hover .remove-btn {
    opacity: 1;
}

.remove-btn:hover {
    background: var(--apple-red);
    color: white;
}
```

### Drag & Drop JavaScript

```javascript
let draggedElement = null;

function initDragAndDrop() {
    const container = document.getElementById('tracked-devices');
    const chips = container.querySelectorAll('.device-chip');
    
    chips.forEach(chip => {
        chip.addEventListener('dragstart', handleDragStart);
        chip.addEventListener('dragend', handleDragEnd);
        chip.addEventListener('dragover', handleDragOver);
        chip.addEventListener('drop', handleDrop);
        chip.addEventListener('dragleave', handleDragLeave);
    });
}

function handleDragStart(e) {
    draggedElement = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
}

function handleDragEnd(e) {
    this.classList.remove('dragging');
    document.querySelectorAll('.device-chip').forEach(chip => {
        chip.classList.remove('drag-over');
    });
    saveDeviceOrder();
}

function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    this.classList.add('drag-over');
}

function handleDragLeave(e) {
    this.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    if (draggedElement !== this) {
        const container = document.getElementById('tracked-devices');
        const allChips = [...container.querySelectorAll('.device-chip')];
        const draggedIdx = allChips.indexOf(draggedElement);
        const targetIdx = allChips.indexOf(this);
        
        if (draggedIdx < targetIdx) {
            this.parentNode.insertBefore(draggedElement, this.nextSibling);
        } else {
            this.parentNode.insertBefore(draggedElement, this);
        }
    }
    this.classList.remove('drag-over');
}

function saveDeviceOrder() {
    const container = document.getElementById('tracked-devices');
    const order = [...container.querySelectorAll('.device-chip')]
        .map(chip => chip.dataset.deviceId);
    localStorage.setItem('device_order', JSON.stringify(order));
}

function loadDeviceOrder() {
    const saved = localStorage.getItem('device_order');
    return saved ? JSON.parse(saved) : null;
}

// On page load, select first device
function selectDefaultDevice() {
    const firstChip = document.querySelector('.device-chip');
    if (firstChip) {
        selectDevice(firstChip.dataset.deviceId);
    }
}
```

---

## Component 3: Minimal Map Popup (Find My Style)

### Design
- Small, minimal popup directly on marker
- Just device name and brief info
- Click marker or popup to show full details in sidebar

```html
<div class="findmy-popup">
    <div class="popup-title">iPhone</div>
    <div class="popup-subtitle">6 min ago</div>
</div>
```

### CSS

```css
.findmy-popup {
    background: var(--bg-elevated);
    border-radius: var(--radius-lg);
    padding: var(--spacing-sm) var(--spacing-md);
    box-shadow: var(--shadow-lg);
    text-align: center;
    min-width: 80px;
}

.popup-title {
    font-size: var(--font-size-footnote);
    font-weight: 600;
    color: var(--text-primary);
}

.popup-subtitle {
    font-size: var(--font-size-caption2);
    color: var(--text-secondary);
}

/* Popup arrow */
.findmy-popup::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 50%;
    transform: translateX(-50%);
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-top: 8px solid var(--bg-elevated);
}

/* Leaflet popup overrides */
.leaflet-popup-content-wrapper {
    background: transparent;
    box-shadow: none;
    padding: 0;
}

.leaflet-popup-tip-container {
    display: none;
}
```

---

## Component 4: Compact Time Navigation

### Design
- Inline with map, bottom overlay
- Compact single-line design
- Play/pause, slider, current time

```html
<div class="time-nav">
    <button class="time-nav-btn" id="play-btn">
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
</div>
```

### CSS

```css
.time-nav {
    position: absolute;
    bottom: var(--spacing-lg);
    left: 50%;
    transform: translateX(-50%);
    background: var(--bg-elevated);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: var(--radius-xl);
    padding: var(--spacing-sm) var(--spacing-md);
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    box-shadow: var(--shadow-lg);
    min-width: 400px;
    max-width: 600px;
}

.time-nav-btn {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: var(--apple-blue);
    border: none;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    flex-shrink: 0;
}

.time-nav-btn:hover {
    background: #0056CC;
}

.time-slider-wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.time-slider-wrapper input[type="range"] {
    width: 100%;
    height: 4px;
    -webkit-appearance: none;
    background: var(--apple-gray4);
    border-radius: 2px;
}

.time-slider-wrapper input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 14px;
    height: 14px;
    background: white;
    border-radius: 50%;
    cursor: pointer;
    box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}

.time-markers {
    display: flex;
    justify-content: space-between;
    font-size: var(--font-size-caption2);
    color: var(--text-tertiary);
}

.time-display {
    text-align: right;
    flex-shrink: 0;
    min-width: 100px;
}

.time-current {
    font-size: var(--font-size-footnote);
    font-weight: 500;
    display: block;
}

.time-points {
    font-size: var(--font-size-caption2);
    color: var(--text-secondary);
}
```

---

## Component 5: Map Controls Overlay

### Design
- Floating controls on map (bottom-left for heatmap, top-right for layers)
- Apple Maps style toggles

```html
<div class="map-controls-left">
    <label class="toggle-control">
        <input type="checkbox" id="heatmap-toggle">
        <span class="toggle-label">Heatmap</span>
    </label>
</div>

<div class="map-controls-right">
    <div class="layer-switcher">
        <button class="layer-btn active" data-layer="street">Map</button>
        <button class="layer-btn" data-layer="satellite">Satellite</button>
    </div>
</div>
```

### CSS

```css
.map-controls-left {
    position: absolute;
    bottom: 80px;
    left: var(--spacing-lg);
    z-index: 1000;
}

.map-controls-right {
    position: absolute;
    top: var(--spacing-lg);
    right: var(--spacing-lg);
    z-index: 1000;
}

.toggle-control {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    background: var(--bg-elevated);
    backdrop-filter: blur(20px);
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--radius-lg);
    cursor: pointer;
    box-shadow: var(--shadow-md);
}

.toggle-control input[type="checkbox"] {
    width: 18px;
    height: 18px;
    accent-color: var(--apple-blue);
}

.toggle-label {
    font-size: var(--font-size-footnote);
    font-weight: 500;
}

.layer-switcher {
    display: flex;
    background: var(--bg-elevated);
    backdrop-filter: blur(20px);
    border-radius: var(--radius-md);
    overflow: hidden;
    box-shadow: var(--shadow-md);
}

.layer-btn {
    padding: var(--spacing-sm) var(--spacing-md);
    background: transparent;
    border: none;
    color: var(--text-primary);
    font-size: var(--font-size-footnote);
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
}

.layer-btn.active {
    background: var(--apple-blue);
    color: white;
}

.layer-btn:hover:not(.active) {
    background: var(--bg-tertiary);
}
```

---

## Component 6: Add Device Modal

### Design
- Modal overlay for adding devices
- Collapsible list of available devices

```html
<div class="modal-overlay" id="add-device-modal">
    <div class="modal">
        <div class="modal-header">
            <h2>Add Device</h2>
            <button class="modal-close">✕</button>
        </div>
        <div class="modal-body">
            <div class="device-list">
                <!-- Available devices -->
            </div>
        </div>
    </div>
</div>
```

---

## Page Layout

### Main HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Location History</title>
    <!-- Styles -->
</head>
<body class="dark-theme">
    <div class="app-container">
        <!-- Sidebar -->
        <aside class="sidebar">
            <header class="sidebar-header">
                <h1>Location History</h1>
            </header>
            
            <section class="devices-section">
                <div class="devices-list" id="tracked-devices">
                    <!-- Draggable device chips -->
                </div>
                <button class="add-device-btn" id="add-device-btn">
                    <span>+</span> Add Device
                </button>
            </section>
            
            <div class="sidebar-divider"></div>
            
            <section class="details-section" id="device-details">
                <!-- Device details populated here -->
            </section>
        </aside>
        
        <!-- Map Container -->
        <main class="map-container">
            <div id="map"></div>
            
            <!-- Map Controls -->
            <div class="map-controls-left">
                <label class="toggle-control">
                    <input type="checkbox" id="heatmap-toggle">
                    <span class="toggle-label">Heatmap</span>
                </label>
            </div>
            
            <div class="map-controls-right">
                <div class="layer-switcher">
                    <button class="layer-btn active" data-layer="street">Map</button>
                    <button class="layer-btn" data-layer="satellite">Satellite</button>
                </div>
            </div>
            
            <!-- Time Navigation -->
            <div class="time-nav">
                <!-- Time controls -->
            </div>
        </main>
    </div>
    
    <!-- Modals -->
    <div class="modal-overlay" id="add-device-modal">
        <!-- Add device modal -->
    </div>
</body>
</html>
```

### Main Layout CSS

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body {
    height: 100%;
    font-family: var(--font-family);
}

.app-container {
    display: flex;
    height: 100vh;
    background: var(--bg-primary);
    color: var(--text-primary);
}

.map-container {
    flex: 1;
    position: relative;
    overflow: hidden;
}

#map {
    width: 100%;
    height: 100%;
}
```

---

## Responsive Behavior

### Mobile (< 768px)
- Sidebar becomes bottom sheet (slide up)
- Time nav becomes full width
- Device chips scroll horizontally

```css
@media (max-width: 768px) {
    .app-container {
        flex-direction: column-reverse;
    }
    
    .sidebar {
        width: 100%;
        height: auto;
        max-height: 50vh;
        border-right: none;
        border-top: 1px solid var(--apple-gray4);
    }
    
    .devices-list {
        flex-direction: row;
        overflow-x: auto;
        gap: var(--spacing-sm);
        padding-bottom: var(--spacing-sm);
    }
    
    .device-chip {
        flex-shrink: 0;
    }
    
    .time-nav {
        left: var(--spacing-md);
        right: var(--spacing-md);
        transform: none;
        min-width: auto;
    }
}
```

---

## Acceptance Criteria

1. Sidebar contains all device details (no large popups on map)
2. Map popup is minimal - just device name and time
3. Clicking map marker shows details in sidebar
4. Device chips are draggable to reorder
5. First device in list is auto-selected on page load
6. Device order persists in localStorage
7. Time navigation is compact, single-line overlay on map
8. Heatmap toggle and layer switcher as floating controls
9. Apple design language throughout (colors, typography, spacing, blur effects)
10. Responsive layout for mobile devices
11. "Add Device" opens modal with available devices
