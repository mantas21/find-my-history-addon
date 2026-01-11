/* eslint-disable @typescript-eslint/no-explicit-any */
/* Home Assistant Find My History Card */

class FindMyHistoryCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.locations = [];
    this.currentTime = null;
    this.playing = false;
    this.playbackSpeed = 1;
    this.selectedDevice = null;
  }

  static getConfigElement() {
    return document.createElement('find-my-history-card-editor');
  }

  static getStubConfig() {
    return {
      devices: [],
      default_time_range: '24h',
      highlight_unknown: true,
      api_url: 'http://localhost:8080',
    };
  }

  setConfig(config) {
    this.config = {
      ...FindMyHistoryCard.getStubConfig(),
      ...config,
    };
    this.render();
    this.loadData();
  }

  set hass(hass) {
    this._hass = hass;
    if (this.locations.length === 0) {
      this.loadData();
    }
  }

  async loadData() {
    if (!this.config.devices || this.config.devices.length === 0) {
      this.showError('No devices configured');
      return;
    }

    try {
      // Calculate time range
      const endTime = new Date();
      const startTime = this.getStartTime(endTime);
      
      // Load data for first device if none selected
      const device = this.selectedDevice || this.config.devices[0];
      
      const apiUrl = this.config.api_url || 'http://localhost:8080';
      const response = await fetch(
        `${apiUrl}/api/locations?device_id=${device}&start=${startTime.toISOString()}&end=${endTime.toISOString()}&limit=10000`
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      this.locations = data.locations || [];
      
      if (this.locations.length === 0) {
        this.showMessage('No location data found for selected time range');
        return;
      }

      // Set current time to latest
      this.currentTime = new Date(this.locations[this.locations.length - 1].time);
      this.render();
      this.updateMap();

    } catch (error) {
      console.error('Error loading location data:', error);
      this.showError(`Failed to load data: ${error.message}`);
    }
  }

  getStartTime(endTime) {
    const range = this.config.default_time_range || '24h';
    const hours = this.parseTimeRange(range);
    return new Date(endTime.getTime() - hours * 60 * 60 * 1000);
  }

  parseTimeRange(range) {
    const match = range.match(/(\d+)([hd])/);
    if (!match) return 24; // Default 24 hours
    
    const value = parseInt(match[1]);
    const unit = match[2];
    
    return unit === 'd' ? value * 24 : value;
  }

  getLocationAtTime(time) {
    if (!this.locations.length) return null;
    
    // Find closest location to given time
    let closest = this.locations[0];
    let minDiff = Math.abs(new Date(closest.time) - time);
    
    for (const loc of this.locations) {
      const diff = Math.abs(new Date(loc.time) - time);
      if (diff < minDiff) {
        minDiff = diff;
        closest = loc;
      }
    }
    
    return closest;
  }

  updateMap() {
    const mapContainer = this.shadowRoot.querySelector('#map-container');
    if (!mapContainer) return;

    const location = this.getLocationAtTime(this.currentTime);
    if (!location) return;

    // Create Leaflet map if not exists
    if (!this.map) {
      this.map = L.map(mapContainer).setView([location.latitude, location.longitude], 13);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(this.map);
      
      // Add path polyline
      this.pathLayer = L.layerGroup().addTo(this.map);
      this.markerLayer = L.layerGroup().addTo(this.map);
    }

    // Update path
    this.pathLayer.clearLayers();
    const pathCoords = this.locations
      .filter(loc => loc.latitude && loc.longitude)
      .map(loc => [loc.latitude, loc.longitude]);
    
    if (pathCoords.length > 1) {
      const path = L.polyline(pathCoords, {
        color: '#3388ff',
        weight: 3,
        opacity: 0.7
      }).addTo(this.pathLayer);
    }

    // Update marker for current location
    this.markerLayer.clearLayers();
    const color = location.in_zone ? 'green' : 'red';
    const icon = L.divIcon({
      className: 'location-marker',
      html: `<div style="background-color: ${color}; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
      iconSize: [20, 20],
      iconAnchor: [10, 10]
    });
    
    L.marker([location.latitude, location.longitude], { icon })
      .addTo(this.markerLayer)
      .bindPopup(`
        <strong>${location.device_name || location.device_id}</strong><br>
        Time: ${new Date(location.time).toLocaleString()}<br>
        Zone: ${location.zone_name || 'Unknown'}<br>
        Location: ${location.latitude.toFixed(4)}, ${location.longitude.toFixed(4)}
      `);

    // Center map on current location
    this.map.setView([location.latitude, location.longitude], 13);
  }

  play() {
    if (this.playing) return;
    
    this.playing = true;
    const startTime = new Date(this.locations[0].time);
    const endTime = new Date(this.locations[this.locations.length - 1].time);
    const duration = endTime - startTime;
    const step = duration / (this.locations.length * 10); // 10 steps per location
    
    this.playInterval = setInterval(() => {
      this.currentTime = new Date(this.currentTime.getTime() + step * this.playbackSpeed);
      
      if (this.currentTime > endTime) {
        this.pause();
        this.currentTime = endTime;
      }
      
      this.updateTimeDisplay();
      this.updateMap();
    }, 100);
  }

  pause() {
    this.playing = false;
    if (this.playInterval) {
      clearInterval(this.playInterval);
      this.playInterval = null;
    }
  }

  updateTimeDisplay() {
    const timeDisplay = this.shadowRoot.querySelector('#time-display');
    if (timeDisplay && this.currentTime) {
      timeDisplay.textContent = this.currentTime.toLocaleString();
    }
  }

  onTimeSliderChange(event) {
    const value = parseFloat(event.target.value);
    const startTime = new Date(this.locations[0].time);
    const endTime = new Date(this.locations[this.locations.length - 1].time);
    const duration = endTime - startTime;
    this.currentTime = new Date(startTime.getTime() + duration * value);
    this.updateTimeDisplay();
    this.updateMap();
  }

  showError(message) {
    const container = this.shadowRoot.querySelector('#card-container');
    if (container) {
      container.innerHTML = `
        <div class="error">
          <ha-icon icon="mdi:alert-circle"></ha-icon>
          <p>${message}</p>
        </div>
      `;
    }
  }

  showMessage(message) {
    const container = this.shadowRoot.querySelector('#card-container');
    if (container) {
      container.innerHTML = `
        <div class="message">
          <ha-icon icon="mdi:information"></ha-icon>
          <p>${message}</p>
        </div>
      `;
    }
  }

  render() {
    this.shadowRoot.innerHTML = `
      <ha-card>
        <div class="card-header">
          <h2>Find My Location History</h2>
        </div>
        <div id="card-container" class="card-content">
          <div id="controls" class="controls">
            <select id="device-selector" class="device-selector">
              ${this.config.devices.map(device => `
                <option value="${device}" ${device === this.selectedDevice ? 'selected' : ''}>
                  ${device}
                </option>
              `).join('')}
            </select>
            <div class="time-controls">
              <button id="play-pause" class="control-btn">
                <ha-icon icon="${this.playing ? 'mdi:pause' : 'mdi:play'}"></ha-icon>
              </button>
              <input type="range" id="time-slider" min="0" max="1" step="0.001" value="1" class="time-slider">
              <span id="time-display" class="time-display"></span>
            </div>
            <div class="stats" id="stats"></div>
          </div>
          <div id="map-container" class="map-container"></div>
        </div>
      </ha-card>
      <style>
        ha-card {
          padding: 16px;
        }
        .card-header h2 {
          margin: 0 0 16px 0;
          font-size: 1.2em;
        }
        .controls {
          margin-bottom: 16px;
        }
        .device-selector {
          width: 100%;
          padding: 8px;
          margin-bottom: 12px;
          border: 1px solid var(--divider-color);
          border-radius: 4px;
        }
        .time-controls {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 12px;
        }
        .control-btn {
          background: var(--primary-color);
          color: var(--text-primary-color);
          border: none;
          border-radius: 50%;
          width: 40px;
          height: 40px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .time-slider {
          flex: 1;
          height: 6px;
        }
        .time-display {
          min-width: 180px;
          font-size: 0.9em;
          color: var(--secondary-text-color);
        }
        .map-container {
          width: 100%;
          height: 400px;
          border-radius: 4px;
          overflow: hidden;
        }
        .stats {
          padding: 8px;
          background: var(--card-background-color);
          border-radius: 4px;
          font-size: 0.9em;
        }
        .error, .message {
          padding: 16px;
          text-align: center;
          color: var(--error-color);
        }
        .message {
          color: var(--primary-text-color);
        }
      </style>
      <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
      <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    `;

    // Attach event listeners
    const deviceSelector = this.shadowRoot.querySelector('#device-selector');
    if (deviceSelector) {
      deviceSelector.addEventListener('change', (e) => {
        this.selectedDevice = e.target.value;
        this.loadData();
      });
    }

    const playPauseBtn = this.shadowRoot.querySelector('#play-pause');
    if (playPauseBtn) {
      playPauseBtn.addEventListener('click', () => {
        if (this.playing) {
          this.pause();
        } else {
          this.play();
        }
        this.render();
      });
    }

    const timeSlider = this.shadowRoot.querySelector('#time-slider');
    if (timeSlider) {
      timeSlider.addEventListener('input', (e) => this.onTimeSliderChange(e));
    }

    this.updateTimeDisplay();
  }
}

customElements.define('find-my-history-card', FindMyHistoryCard);
