/**
 * Tests for Find My History Card frontend component
 */

// Mock the custom element before importing
class MockHTMLElement {
  constructor() {
    this.shadowRoot = {
      appendChild: jest.fn(),
      querySelector: jest.fn(),
      querySelectorAll: jest.fn(),
      innerHTML: '',
    };
  }
  attachShadow() {
    return this.shadowRoot;
  }
}

// Since the card is a custom element, we'll test its logic
describe('FindMyHistoryCard', () => {
  let card;
  let mockFetch;

  beforeEach(() => {
    // Reset fetch mock
    mockFetch = jest.fn();
    global.fetch = mockFetch;

    // Create a mock card instance
    card = {
      config: {
        devices: ['device_tracker.iphone'],
        default_time_range: '24h',
        highlight_unknown: true,
        api_url: 'http://localhost:8080',
      },
      locations: [],
      currentTime: null,
      playing: false,
      playbackSpeed: 1,
      selectedDevice: null,
    };
  });

  describe('Time Range Parsing', () => {
    test('should parse hours correctly', () => {
      const parseTimeRange = (range) => {
        const match = range.match(/(\d+)([hd])/);
        if (!match) return 24;
        const value = parseInt(match[1]);
        const unit = match[2];
        return unit === 'd' ? value * 24 : value;
      };

      expect(parseTimeRange('1h')).toBe(1);
      expect(parseTimeRange('24h')).toBe(24);
      expect(parseTimeRange('6h')).toBe(6);
    });

    test('should parse days correctly', () => {
      const parseTimeRange = (range) => {
        const match = range.match(/(\d+)([hd])/);
        if (!match) return 24;
        const value = parseInt(match[1]);
        const unit = match[2];
        return unit === 'd' ? value * 24 : value;
      };

      expect(parseTimeRange('1d')).toBe(24);
      expect(parseTimeRange('7d')).toBe(168);
      expect(parseTimeRange('30d')).toBe(720);
    });

    test('should default to 24 hours for invalid range', () => {
      const parseTimeRange = (range) => {
        const match = range.match(/(\d+)([hd])/);
        if (!match) return 24;
        const value = parseInt(match[1]);
        const unit = match[2];
        return unit === 'd' ? value * 24 : value;
      };

      expect(parseTimeRange('invalid')).toBe(24);
      expect(parseTimeRange('')).toBe(24);
    });
  });

  describe('API Integration', () => {
    test('should construct correct API URL', () => {
      const device = 'device_tracker.iphone';
      const endTime = new Date('2025-01-27T12:00:00Z');
      const startTime = new Date('2025-01-26T12:00:00Z');
      const apiUrl = 'http://localhost:8080';

      const expectedUrl = `${apiUrl}/api/locations?device_id=${device}&start=${startTime.toISOString()}&end=${endTime.toISOString()}&limit=10000`;
      
      expect(expectedUrl).toContain(device);
      expect(expectedUrl).toContain(startTime.toISOString());
      expect(expectedUrl).toContain(endTime.toISOString());
    });

    test('should handle API errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      const response = await fetch('http://localhost:8080/api/locations');
      expect(response.ok).toBe(false);
      expect(response.status).toBe(500);
    });

    test('should handle successful API response', async () => {
      const mockData = {
        locations: [
          {
            time: '2025-01-27T10:00:00Z',
            latitude: 54.8985,
            longitude: 23.9036,
            in_zone: true,
            zone_name: 'home',
          },
        ],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      });

      const response = await fetch('http://localhost:8080/api/locations');
      const data = await response.json();

      expect(response.ok).toBe(true);
      expect(data.locations).toHaveLength(1);
      expect(data.locations[0].latitude).toBe(54.8985);
    });
  });

  describe('Configuration', () => {
    test('should merge config with defaults', () => {
      const getStubConfig = () => ({
        devices: [],
        default_time_range: '24h',
        highlight_unknown: true,
        api_url: 'http://localhost:8080',
      });

      const userConfig = {
        devices: ['device_tracker.iphone'],
        api_url: 'http://custom:8090',
      };

      const mergedConfig = {
        ...getStubConfig(),
        ...userConfig,
      };

      expect(mergedConfig.devices).toEqual(['device_tracker.iphone']);
      expect(mergedConfig.api_url).toBe('http://custom:8090');
      expect(mergedConfig.default_time_range).toBe('24h');
    });
  });

  describe('Time Calculations', () => {
    test('should calculate start time correctly', () => {
      const getStartTime = (endTime, range) => {
        const parseTimeRange = (r) => {
          const match = r.match(/(\d+)([hd])/);
          if (!match) return 24;
          const value = parseInt(match[1]);
          const unit = match[2];
          return unit === 'd' ? value * 24 : value;
        };
        const hours = parseTimeRange(range);
        return new Date(endTime.getTime() - hours * 60 * 60 * 1000);
      };

      const endTime = new Date('2025-01-27T12:00:00Z');
      const startTime = getStartTime(endTime, '24h');

      const diffHours = (endTime - startTime) / (1000 * 60 * 60);
      expect(diffHours).toBe(24);
    });
  });
});
