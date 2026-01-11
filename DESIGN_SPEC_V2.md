# Find My Location History - Design Specification v2

## Project Context

**File to modify:** `find_my_history_addon/www/index.html`

**Prerequisite:** v1 features (tracked device buttons, collapsible devices, heatmap) are already implemented.

---

## Feature: Enhanced Location Popup

**Current behavior:** Popup shows basic info - device name, timestamp, zone, coordinates.

**Goal:** Show how long device stayed at this location and where they came from.

---

### Improved Popup Layout

**Current popup (hard to read):**
```
Viktorija's iPhone
Time: 11/01/2026, 12:50:12
Zone: Unknown
Coords: 54.71881, 25.30142
```

**New popup (cleaner UX with business names):**
```
┌─────────────────────────────────┐
│  Viktorija's iPhone             │
├─────────────────────────────────┤
│  📍 Caffeine Vilnius            │  <- Nearby business name
│     Gedimino pr. 9              │  <- Street address
├─────────────────────────────────┤
│  🕐 Today, 12:50                │
│  ⏱️ Here for 1h 23m             │
├─────────────────────────────────┤
│  ← From: Home                   │
│     2.4 km away                 │
└─────────────────────────────────┘
```

---

### Nearby Business Lookup (Google Places API)

**Goal:** Replace raw coordinates with the nearest popular business/place name within 20 meters.

**Priority order for location display:**
1. Known Home Assistant zone (Home, Work, etc.) - if within zone
2. Nearby business name from Google Places (within 20m)
3. Street address from reverse geocoding
4. Raw coordinates as fallback

**API Requirements:**
- Google Places API key (configured in addon settings)
- Nearby Search endpoint: `https://maps.googleapis.com/maps/api/place/nearbysearch/json`

**API Call:**
```javascript
async function getNearbyPlace(lat, lng, apiKey) {
    const radius = 20; // meters
    const url = `https://maps.googleapis.com/maps/api/place/nearbysearch/json?` +
                `location=${lat},${lng}&radius=${radius}&key=${apiKey}`;
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.results && data.results.length > 0) {
            // Sort by popularity (rating * user_ratings_total)
            const sorted = data.results.sort((a, b) => {
                const scoreA = (a.rating || 0) * (a.user_ratings_total || 0);
                const scoreB = (b.rating || 0) * (b.user_ratings_total || 0);
                return scoreB - scoreA;
            });
            
            const best = sorted[0];
            return {
                name: best.name,
                address: best.vicinity,
                types: best.types,
                rating: best.rating
            };
        }
        return null;
    } catch (error) {
        console.error('Places API error:', error);
        return null;
    }
}
```

**Fallback: Reverse Geocoding for Street Address**
```javascript
async function getStreetAddress(lat, lng, apiKey) {
    const url = `https://maps.googleapis.com/maps/api/geocode/json?` +
                `latlng=${lat},${lng}&key=${apiKey}`;
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.results && data.results.length > 0) {
            // Get the most specific address (usually first result)
            return data.results[0].formatted_address;
        }
        return null;
    } catch (error) {
        return null;
    }
}
```

**Caching Strategy:**
- Cache API results by location cluster (100m grid)
- Store in localStorage with TTL of 7 days
- Avoids repeated API calls for same locations
- Reduces API costs

```javascript
const CACHE_KEY = 'places_cache';
const CACHE_TTL = 7 * 24 * 60 * 60 * 1000; // 7 days

function getCacheKey(lat, lng) {
    // Round to ~100m grid for cache hits on nearby points
    return `${lat.toFixed(3)},${lng.toFixed(3)}`;
}

function getCachedPlace(lat, lng) {
    const cache = JSON.parse(localStorage.getItem(CACHE_KEY) || '{}');
    const key = getCacheKey(lat, lng);
    const entry = cache[key];
    
    if (entry && Date.now() - entry.timestamp < CACHE_TTL) {
        return entry.data;
    }
    return null;
}

function cachePlace(lat, lng, placeData) {
    const cache = JSON.parse(localStorage.getItem(CACHE_KEY) || '{}');
    const key = getCacheKey(lat, lng);
    cache[key] = { data: placeData, timestamp: Date.now() };
    localStorage.setItem(CACHE_KEY, JSON.stringify(cache));
}
```

**Configuration (add to addon config.json):**
```json
{
    "google_places_api_key": "str?"
}
```

**Display Logic:**
```javascript
async function getLocationDisplayName(location, apiKey) {
    // 1. Check if in known HA zone
    if (location.in_zone && location.zone_name) {
        return {
            primary: location.zone_name,
            secondary: null,
            icon: '🏠'
        };
    }
    
    // 2. Check cache first
    const cached = getCachedPlace(location.latitude, location.longitude);
    if (cached) {
        return cached;
    }
    
    // 3. Try Google Places API
    if (apiKey) {
        const place = await getNearbyPlace(location.latitude, location.longitude, apiKey);
        if (place) {
            const result = {
                primary: place.name,
                secondary: place.address,
                icon: '📍'
            };
            cachePlace(location.latitude, location.longitude, result);
            return result;
        }
        
        // 4. Fallback to street address
        const address = await getStreetAddress(location.latitude, location.longitude, apiKey);
        if (address) {
            const result = {
                primary: address.split(',')[0], // Street name
                secondary: address.split(',').slice(1).join(',').trim(),
                icon: '📍'
            };
            cachePlace(location.latitude, location.longitude, result);
            return result;
        }
    }
    
    // 5. Final fallback: coordinates
    return {
        primary: 'Unknown location',
        secondary: `${location.latitude.toFixed(4)}, ${location.longitude.toFixed(4)}`,
        icon: '📍'
    };
}
```

**Free Alternative (OpenStreetMap Nominatim):**

If Google API is not configured, use free Nominatim:

```javascript
async function getNominatimPlace(lat, lng) {
    const url = `https://nominatim.openstreetmap.org/reverse?` +
                `lat=${lat}&lon=${lng}&format=json&addressdetails=1&zoom=18`;
    
    try {
        const response = await fetch(url, {
            headers: { 'User-Agent': 'FindMyHistory/1.0' }
        });
        const data = await response.json();
        
        // Nominatim returns POI name in 'name' or address components
        const name = data.name || 
                     data.address?.amenity || 
                     data.address?.shop ||
                     data.address?.tourism ||
                     data.address?.building;
        
        const road = data.address?.road || data.address?.street;
        
        return {
            primary: name || road || 'Unknown',
            secondary: road && name ? road : null,
            icon: '📍'
        };
    } catch (error) {
        return null;
    }
}
```

**Rate limiting for Nominatim:** Max 1 request per second (use queue/debounce)

---

### Time Display Improvements

**Format timestamps contextually:**

| Condition | Display |
|-----------|---------|
| Today | `Today, 14:30` |
| Yesterday | `Yesterday, 09:15` |
| This week | `Monday, 18:45` |
| Older | `Jan 5, 14:30` |

**Format durations naturally:**

| Duration | Display |
|----------|---------|
| < 1 minute | `< 1 min` |
| 1-59 minutes | `23 min` |
| 1-24 hours | `1h 45m` |
| > 24 hours | `2d 3h` |

---

### Duration Calculation

**Definition:** Time spent within 100 meters of the selected point.

**Algorithm:**
```javascript
function calculateDuration(locations, currentIndex) {
    const current = locations[currentIndex];
    const RADIUS = 100; // meters
    
    // Find first point in this cluster (going backwards)
    let startIndex = currentIndex;
    while (startIndex > 0) {
        const prev = locations[startIndex - 1];
        if (getDistance(current, prev) > RADIUS) break;
        startIndex--;
    }
    
    // Find last point in this cluster (going forwards)
    let endIndex = currentIndex;
    while (endIndex < locations.length - 1) {
        const next = locations[endIndex + 1];
        if (getDistance(current, next) > RADIUS) break;
        endIndex++;
    }
    
    const arrival = new Date(locations[startIndex].time);
    const departure = new Date(locations[endIndex].time);
    return departure - arrival; // milliseconds
}
```

**Haversine distance function:**
```javascript
function getDistance(loc1, loc2) {
    const R = 6371000; // Earth radius in meters
    const lat1 = loc1.latitude * Math.PI / 180;
    const lat2 = loc2.latitude * Math.PI / 180;
    const dLat = (loc2.latitude - loc1.latitude) * Math.PI / 180;
    const dLon = (loc2.longitude - loc1.longitude) * Math.PI / 180;
    
    const a = Math.sin(dLat/2) ** 2 +
              Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon/2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
}
```

---

### Previous Stable Location

**Definition:** A location where the device stayed for at least 30 minutes before arriving at the current location.

**Purpose:** Filter out transit (walking/driving) to show meaningful "came from" info.

**Algorithm:**
```javascript
function findPreviousStableLocation(locations, currentIndex) {
    const current = locations[currentIndex];
    const RADIUS = 100; // meters
    const MIN_STABLE_TIME = 30 * 60 * 1000; // 30 minutes in ms
    
    // Step 1: Skip past current location cluster
    let searchIndex = currentIndex;
    while (searchIndex > 0) {
        const prev = locations[searchIndex - 1];
        if (getDistance(current, prev) > RADIUS) break;
        searchIndex--;
    }
    searchIndex--; // Move to first point outside current cluster
    
    // Step 2: Search backwards for a stable location
    while (searchIndex >= 0) {
        const candidate = locations[searchIndex];
        
        // Find cluster boundaries for this candidate
        let clusterStart = searchIndex;
        while (clusterStart > 0) {
            if (getDistance(candidate, locations[clusterStart - 1]) > RADIUS) break;
            clusterStart--;
        }
        
        let clusterEnd = searchIndex;
        while (clusterEnd < locations.length - 1) {
            if (getDistance(candidate, locations[clusterEnd + 1]) > RADIUS) break;
            clusterEnd++;
        }
        
        // Check if stable (30+ minutes)
        const duration = new Date(locations[clusterEnd].time) - 
                        new Date(locations[clusterStart].time);
        
        if (duration >= MIN_STABLE_TIME) {
            return {
                location: candidate,
                zoneName: candidate.zone_name || null,
                distance: getDistance(current, candidate),
                duration: duration
            };
        }
        
        // Move to before this cluster and continue searching
        searchIndex = clusterStart - 1;
    }
    
    return null; // No previous stable location found
}
```

---

### Display Logic

**Previous location text:**

| Scenario | Display |
|----------|---------|
| Has zone name | `← From: Home` / `← From: Work` |
| No zone (coords) | `← From: 54.7123, 25.2456` |
| Not found | Hide this section entirely |
| First location in history | `← Start of tracking` |

**Distance formatting:**

| Distance | Display |
|----------|---------|
| < 1 km | `850 m away` |
| >= 1 km | `2.4 km away` |

---

### Popup HTML Structure

```html
<div class="location-popup">
    <div class="popup-header">
        <strong class="device-name">Viktorija's iPhone</strong>
    </div>
    
    <div class="popup-section location">
        <div class="place-name">📍 Caffeine Vilnius</div>
        <div class="place-address">Gedimino pr. 9</div>
    </div>
    
    <div class="popup-section timing">
        <div class="timestamp">🕐 Today, 12:50</div>
        <div class="duration">⏱️ Here for 1h 23m</div>
    </div>
    
    <div class="popup-section origin">
        <div class="from-label">← From: Home</div>
        <div class="from-distance">2.4 km away</div>
    </div>
</div>
```

---

### Popup CSS

```css
.location-popup {
    min-width: 200px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.popup-header {
    padding-bottom: 8px;
    border-bottom: 1px solid #ddd;
    margin-bottom: 8px;
}

.device-name {
    font-size: 14px;
    font-weight: 600;
}

.popup-section {
    margin-bottom: 8px;
    padding-bottom: 8px;
    border-bottom: 1px solid #eee;
}

.popup-section:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
}

.place-name {
    font-weight: 500;
    margin-bottom: 2px;
}

.place-address {
    font-size: 12px;
    color: #666;
}

.timestamp {
    margin-bottom: 2px;
}

.duration {
    font-weight: 500;
    color: #0066cc;
}

.from-label {
    font-weight: 500;
}

.from-distance {
    font-size: 12px;
    color: #666;
}
```

---

## Helper Functions Summary

```javascript
// Add these utility functions to the codebase:

function formatTimestamp(date) {
    const now = new Date();
    const d = new Date(date);
    const isToday = d.toDateString() === now.toDateString();
    const isYesterday = d.toDateString() === new Date(now - 86400000).toDateString();
    const time = d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
    
    if (isToday) return `Today, ${time}`;
    if (isYesterday) return `Yesterday, ${time}`;
    
    const daysDiff = Math.floor((now - d) / 86400000);
    if (daysDiff < 7) {
        return d.toLocaleDateString('en-US', { weekday: 'long' }) + `, ${time}`;
    }
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) + `, ${time}`;
}

function formatDuration(ms) {
    const minutes = Math.floor(ms / 60000);
    if (minutes < 1) return '< 1 min';
    if (minutes < 60) return `${minutes} min`;
    
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours < 24) return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
    
    const days = Math.floor(hours / 24);
    const hrs = hours % 24;
    return hrs > 0 ? `${days}d ${hrs}h` : `${days}d`;
}

function formatDistance(meters) {
    if (meters < 1000) return `${Math.round(meters)} m away`;
    return `${(meters / 1000).toFixed(1)} km away`;
}
```

---

## Acceptance Criteria

1. Popup shows timestamp in contextual format (Today/Yesterday/Weekday/Date)
2. Popup shows duration at location ("Here for Xh Ym")
3. Duration calculated using 100m radius clustering
4. Popup shows previous stable location (30+ min stay) with zone name or business name
5. Distance to previous location displayed
6. Clean visual separation between popup sections
7. Graceful handling of edge cases (no previous location, first point, etc.)
8. Location shows nearby business name (within 20m) instead of raw coordinates
9. Falls back to street address if no business found
10. Falls back to coordinates only if no API key or no results
11. API results cached in localStorage to reduce API calls
12. Works with Google Places API (preferred) or OpenStreetMap Nominatim (free fallback)
