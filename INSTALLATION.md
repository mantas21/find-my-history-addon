# Installation Guide

## Step-by-Step Installation

### 1. Add Custom Repository

1. Open Home Assistant in your browser
2. Go to **Supervisor** → **Add-on Store**
3. Click the **three dots (⋮)** in the top right corner
4. Select **Repositories**
5. Add repository URL: `https://github.com/mantas21/find-my-history-addon`
6. Click **Add**

### 2. Install the Add-on

1. Find "Find My Location History" in the add-on store
2. Click on it
3. Click **Install**
4. Wait for installation to complete

### 3. Get Required Credentials

#### Long-Lived Access Token

1. Go to Home Assistant → **Settings** → **People**
2. Scroll to **Long-lived access tokens**
3. Click **Create Token**
4. Name: "Find My History Add-on"
5. Copy the token (you'll only see it once!)

#### InfluxDB Password

1. Go to **Supervisor** → **Add-ons** → **InfluxDB**
2. Click **Configuration** tab
3. Note your InfluxDB username and password

#### Device Tracker IDs

1. Go to **Settings** → **Devices & Services** → **iCloud**
2. Click **Entities** tab
3. Note the entity IDs starting with `device_tracker.`

### 4. Configure the Add-on

1. Go to **Supervisor** → **Add-ons** → **Find My Location History**
2. Click **Configuration** tab
3. Fill in your settings:

```yaml
ha_url: http://supervisor/core
ha_token: YOUR_LONG_LIVED_TOKEN_HERE
check_interval: 30
devices:
  - device_tracker.iphone
  - device_tracker.ipad
influxdb_host: a0d7b954_influxdb
influxdb_port: 8086
influxdb_database: find_my_history
influxdb_username: admin
influxdb_password: YOUR_INFLUXDB_PASSWORD
focus_unknown_locations: true
api_port: 8090
```

4. Click **Save**

### 5. Create InfluxDB Database

**Via InfluxDB UI:**
1. Open InfluxDB add-on Web UI
2. Go to Data Explorer
3. Run: `CREATE DATABASE find_my_history`

**Via Command Line:**
```bash
curl -X POST "http://a0d7b954_influxdb:8086/query?u=admin&p=YOUR_PASSWORD" \
  --data-urlencode "q=CREATE DATABASE find_my_history"
```

### 6. Start the Add-on

1. Go to **Info** tab
2. Click **Start**
3. Check **Log** tab for:
   - "Configuration loaded: X devices configured"
   - "Loaded X zones"
   - "Starting API server on port 8090"
   - Location storage messages

### 7. Install Lovelace Card

**Copy the card file:**
```bash
# From add-on directory
cp www/find-my-history-card.js /config/www/
```

**Or via SSH:**
1. SSH into Home Assistant
2. Run: `cp /addons/local/find_my_history/www/find-my-history-card.js /homeassistant/www/`

**Add as resource:**
1. Settings → Dashboards → Resources
2. Click **Add Resource**
3. URL: `/local/find-my-history-card.js`
4. Type: **JavaScript Module**
5. Click **Create**

### 8. Add Card to Dashboard

1. Edit your dashboard
2. Click **Add Card**
3. Select **Custom: Find My History Card** or use Manual
4. Add YAML:

```yaml
type: custom:find-my-history-card
devices:
  - device_tracker.iphone
  - device_tracker.ipad
default_time_range: 24h
highlight_unknown: true
api_url: http://localhost:8090
```

5. Click **Save**

## Verification

### Check Add-on Status
```bash
ha addons info local_find_my_history
```

### Test API
```bash
curl http://localhost:8090/api/health
```
Should return: `{"status": "ok"}`

### Check Logs
```bash
ha addons logs local_find_my_history
```

### Verify Data in InfluxDB
1. Open InfluxDB Web UI
2. Query: `SELECT * FROM device_location LIMIT 10`
3. You should see location data after first poll

## Troubleshooting

See [README.md#troubleshooting](README.md#troubleshooting) for common issues and solutions.
