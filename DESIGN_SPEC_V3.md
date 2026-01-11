# Find My Location History - Design Specification v3

## Project Context

**Files to modify:**
- `find_my_history_addon/www/index.html` - Frontend UI
- `find_my_history_addon/find_my_history/main.py` - Add battery to polling
- `find_my_history_addon/find_my_history/influxdb_client.py` - Store battery data
- `find_my_history_addon/find_my_history/api.py` - Expose battery in API

**Theme:** Apple ecosystem design language (iOS/macOS style)

---

## Feature 1: Battery Level Tracking

### Backend Changes

**1.1 Extract battery from device_tracker**

iCloud device_tracker entities include `battery_level` in attributes. Modify `extract_location_data()` in `main.py`:

```python
def extract_location_data(entity_state: Dict) -> Optional[Dict]:
    # ... existing code ...
    
    return {
        "latitude": float(latitude),
        "longitude": float(longitude),
        "accuracy": attributes.get("gps_accuracy"),
        "altitude": attributes.get("altitude"),
        "battery_level": attributes.get("battery_level"),  # NEW
        "battery_state": attributes.get("battery_state"),  # charging/not_charging
        "timestamp": timestamp,
    }
```

**1.2 Store battery in InfluxDB**

Add battery fields to `write_location()` in `influxdb_client.py`:

```python
def write_location(self, ..., battery_level=None, battery_state=None):
    fields = {
        "latitude": latitude,
        "longitude": longitude,
        # ... existing fields ...
        "battery_level": battery_level,      # NEW: 0-100 integer
        "battery_state": battery_state,      # NEW: "charging" or "not_charging"
    }
```

**1.3 Include battery in API response**

Ensure `/api/locations` returns battery data for each point.

---

## Feature 2: Apple-Style UI/UX

### Design Tokens (CSS Variables)

```css
:root {
    /* Apple System Colors */
    --apple-blue: #007AFF;
    --apple-green: #34C759;
    --apple-yellow: #FF9500;
    --apple-red: #FF3B30;
    --apple-gray: #8E8E93;
    --apple-gray2: #636366;
    --apple-gray3: #48484A;
    --apple-gray4: #3A3A3C;
    --apple-gray5: #2C2C2E;
    --apple-gray6: #1C1C1E;
    
    /* Backgrounds */
    --bg-primary: #000000;
    --bg-secondary: #1C1C1E;
    --bg-tertiary: #2C2C2E;
    --bg-elevated: #3A3A3C;
    
    /* Text */
    --text-primary: #FFFFFF;
    --text-secondary: #8E8E93;
    --text-tertiary: #636366;
    
    /* Typography - SF Pro style */
    --font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', sans-serif;
    --font-size-caption2: 11px;
    --font-size-caption: 12px;
    --font-size-footnote: 13px;
    --font-size-subhead: 15px;
    --font-size-body: 17px;
    --font-size-title3: 20px;
    --font-size-title2: 22px;
    --font-size-title: 28px;
    --font-size-largeTitle: 34px;
    
    /* Spacing */
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 12px;
    --spacing-lg: 16px;
    --spacing-xl: 20px;
    
    /* Border Radius */
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
    
    /* Shadows */
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
    --shadow-lg: 0 8px 24px rgba(0,0,0,0.5);
}
```

### Battery Colors (Apple Standard)

| Battery % | Color | CSS Variable |
|-----------|-------|--------------|
| 100-20% | Green | `--apple-green` (#34C759) |
| 20-10% | Yellow | `--apple-yellow` (#FF9500) |
| Below 10% | Red | `--apple-red` (#FF3B30) |
| Charging | Green + ⚡ | `--apple-green` with bolt icon |

```javascript
function getBatteryColor(level, isCharging) {
    if (isCharging) return 'var(--apple-green)';
    if (level > 20) return 'var(--apple-green)';
    if (level > 10) return 'var(--apple-yellow)';
    return 'var(--apple-red)';
}
```

---

## Feature 3: Enhanced Popup (Apple Style)

### Visual Design

```
┌────────────────────────────────────────┐
│                                        │
│  iPhone                    │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━     │
│                                        │
│  📍 Caffeine Vilnius                   │
│     Gedimino pr. 9, Vilnius            │
│                                        │
│  ─────────────────────────────────     │
│                                        │
│  🕐  Today, 12:50                      │
│  ⏱️  Here for 1h 23m                   │
│                                        │
│  ─────────────────────────────────     │
│                                        │
│  ← From: Home · 2.4 km                 │
│                                        │
│  ─────────────────────────────────     │
│                                        │
│  🔋 78%  ████████████░░░░              │  <- Battery bar
│                                        │
│  ─────────────────────────────────     │
│                                        │
│  Last updated: 2 min ago               │
│                                        │
│  ┌──────────────────────────────┐      │
│  │       ↻  Update Now          │      │  <- Action button
│  └──────────────────────────────┘      │
│                                        │
└────────────────────────────────────────┘
```

### Popup HTML Structure

```html
<div class="apple-popup">
    <div class="popup-header">
        <h3 class="device-name">iPhone</h3>
    </div>
    
    <div class="popup-section">
        <div class="location-icon">📍</div>
        <div class="location-details">
            <div class="place-name">Caffeine Vilnius</div>
            <div class="place-address">Gedimino pr. 9, Vilnius</div>
        </div>
    </div>
    
    <div class="popup-divider"></div>
    
    <div class="popup-section timing">
        <div class="timing-row">
            <span class="timing-icon">🕐</span>
            <span class="timing-value">Today, 12:50</span>
        </div>
        <div class="timing-row">
            <span class="timing-icon">⏱️</span>
            <span class="timing-value">Here for 1h 23m</span>
        </div>
    </div>
    
    <div class="popup-divider"></div>
    
    <div class="popup-section origin">
        <span class="origin-arrow">←</span>
        <span class="origin-text">From: Home</span>
        <span class="origin-distance">2.4 km</span>
    </div>
    
    <div class="popup-divider"></div>
    
    <div class="popup-section battery">
        <div class="battery-icon">🔋</div>
        <div class="battery-info">
            <div class="battery-percentage">78%</div>
            <div class="battery-bar">
                <div class="battery-fill" style="width: 78%; background: var(--apple-green);"></div>
            </div>
        </div>
        <div class="charging-indicator" style="display: none;">⚡</div>
    </div>
    
    <div class="popup-divider"></div>
    
    <div class="popup-section meta">
        <div class="last-updated">Last updated: 2 min ago</div>
    </div>
    
    <button class="update-button" onclick="updateDeviceLocation()">
        <span class="update-icon">↻</span>
        Update Now
    </button>
</div>
```

### Popup CSS (Apple Style)

```css
.apple-popup {
    font-family: var(--font-family);
    background: var(--bg-secondary);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    min-width: 280px;
    max-width: 320px;
    color: var(--text-primary);
    box-shadow: var(--shadow-lg);
}

.popup-header {
    margin-bottom: var(--spacing-md);
}

.device-name {
    font-size: var(--font-size-title3);
    font-weight: 600;
    margin: 0;
    letter-spacing: -0.5px;
}

.popup-divider {
    height: 1px;
    background: var(--apple-gray4);
    margin: var(--spacing-md) 0;
}

.popup-section {
    display: flex;
    align-items: flex-start;
    gap: var(--spacing-sm);
}

.location-icon {
    font-size: 20px;
    flex-shrink: 0;
}

.place-name {
    font-size: var(--font-size-body);
    font-weight: 500;
}

.place-address {
    font-size: var(--font-size-footnote);
    color: var(--text-secondary);
    margin-top: 2px;
}

.timing {
    flex-direction: column;
    gap: var(--spacing-xs);
}

.timing-row {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.timing-icon {
    width: 24px;
    text-align: center;
}

.timing-value {
    font-size: var(--font-size-subhead);
}

.origin {
    font-size: var(--font-size-subhead);
}

.origin-arrow {
    color: var(--apple-blue);
    font-weight: 600;
}

.origin-distance {
    color: var(--text-secondary);
    margin-left: auto;
}

/* Battery Section */
.battery {
    align-items: center;
}

.battery-icon {
    font-size: 20px;
}

.battery-info {
    flex: 1;
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.battery-percentage {
    font-size: var(--font-size-subhead);
    font-weight: 600;
    min-width: 40px;
}

.battery-bar {
    flex: 1;
    height: 8px;
    background: var(--apple-gray4);
    border-radius: 4px;
    overflow: hidden;
}

.battery-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s ease;
}

.charging-indicator {
    font-size: 16px;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* Meta Section */
.last-updated {
    font-size: var(--font-size-caption);
    color: var(--text-tertiary);
    text-align: center;
    width: 100%;
}

/* Update Button */
.update-button {
    width: 100%;
    margin-top: var(--spacing-md);
    padding: var(--spacing-md);
    background: var(--apple-blue);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    font-family: var(--font-family);
    font-size: var(--font-size-subhead);
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-sm);
    transition: background 0.2s ease, transform 0.1s ease;
}

.update-button:hover {
    background: #0056CC;
}

.update-button:active {
    transform: scale(0.98);
}

.update-button.loading {
    opacity: 0.7;
    pointer-events: none;
}

.update-icon {
    font-size: 18px;
}

.update-button.loading .update-icon {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
```

---

## Feature 4: Update Now Functionality

### API Endpoint

Add new endpoint to `api.py`:

```python
@app.route('/api/devices/{device_id}/update', methods=['POST'])
async def update_device_location(device_id: str):
    """Force refresh location for a specific device."""
    try:
        # Get current state from HA
        entity_state = ha_client.get_device_tracker_state(device_id)
        if not entity_state:
            return {'error': 'Device not found'}, 404
        
        # Extract and store location
        location_data = extract_location_data(entity_state)
        if not location_data:
            return {'error': 'No location data available'}, 400
        
        # Check zone
        in_zone, zone_name = zone_detector.check_zone(
            location_data["latitude"],
            location_data["longitude"]
        )
        
        # Store in InfluxDB
        success = influx_client.write_location(
            device_id=device_id,
            device_name=entity_state.get("attributes", {}).get("friendly_name", device_id),
            latitude=location_data["latitude"],
            longitude=location_data["longitude"],
            accuracy=location_data.get("accuracy"),
            altitude=location_data.get("altitude"),
            battery_level=location_data.get("battery_level"),
            battery_state=location_data.get("battery_state"),
            in_zone=in_zone,
            zone_name=zone_name,
            timestamp=location_data["timestamp"]
        )
        
        if success:
            return {
                'success': True,
                'location': {
                    'latitude': location_data["latitude"],
                    'longitude': location_data["longitude"],
                    'battery_level': location_data.get("battery_level"),
                    'battery_state': location_data.get("battery_state"),
                    'zone_name': zone_name,
                    'timestamp': location_data["timestamp"].isoformat()
                }
            }
        else:
            return {'error': 'Failed to store location'}, 500
            
    except Exception as e:
        return {'error': str(e)}, 500
```

### Frontend JavaScript

```javascript
async function updateDeviceLocation() {
    const button = document.querySelector('.update-button');
    button.classList.add('loading');
    button.disabled = true;
    
    try {
        const response = await fetch(`./api/devices/${selectedDeviceId}/update`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Refresh the map and data
            await loadData();
            
            // Update last updated time in popup
            updateLastUpdatedTime(new Date());
            
            // Show success feedback
            showToast('Location updated');
        } else {
            showToast(result.error || 'Update failed', 'error');
        }
    } catch (error) {
        showToast('Failed to update location', 'error');
    } finally {
        button.classList.remove('loading');
        button.disabled = false;
    }
}

function updateLastUpdatedTime(date) {
    const element = document.querySelector('.last-updated');
    if (element) {
        element.textContent = `Last updated: ${formatRelativeTime(date)}`;
    }
}

function formatRelativeTime(date) {
    const now = new Date();
    const diff = Math.floor((now - date) / 1000); // seconds
    
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)} min ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return date.toLocaleDateString();
}
```

---

## Feature 5: Toast Notifications (Apple Style)

```html
<div id="toast-container"></div>
```

```css
#toast-container {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 10000;
}

.toast {
    background: var(--bg-elevated);
    color: var(--text-primary);
    padding: var(--spacing-md) var(--spacing-xl);
    border-radius: var(--radius-xl);
    font-family: var(--font-family);
    font-size: var(--font-size-subhead);
    font-weight: 500;
    box-shadow: var(--shadow-lg);
    animation: toastIn 0.3s ease, toastOut 0.3s ease 2.7s;
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.toast.error {
    background: var(--apple-red);
}

.toast.success {
    background: var(--apple-green);
}

@keyframes toastIn {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes toastOut {
    from { opacity: 1; }
    to { opacity: 0; }
}
```

```javascript
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}
```

---

## Acceptance Criteria

1. Battery level is extracted from device_tracker and stored in InfluxDB
2. Battery level shown in popup with Apple-style color coding (green/yellow/red)
3. Battery bar visualization matches Apple design
4. Charging state shown with ⚡ icon when applicable
5. "Last updated: X min ago" shown in popup with relative time
6. "Update Now" button triggers immediate location refresh
7. Button shows loading state during update
8. Toast notification confirms update success/failure
9. All UI elements follow Apple design language (colors, typography, spacing)
10. Dark theme consistent with iOS dark mode
