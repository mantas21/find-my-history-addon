# Frontend Testing

Tests for the JavaScript frontend (Find My History Card).

## Setup

```bash
cd tests/frontend
npm install
```

## Running Tests

```bash
# Run all tests
npm test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run in CI mode
npm run test:ci
```

## Test Structure

- `__tests__/find-my-history-card.test.js` - Tests for the main card component

## Coverage

Target: 70%+ coverage for frontend code.

## Notes

- Tests use Jest with jsdom environment
- Mock fetch for API calls
- Test component logic and utilities
- Integration with Leaflet.js is tested manually
