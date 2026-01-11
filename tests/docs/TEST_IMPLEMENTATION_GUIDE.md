# Test Implementation Guide - Quick Start

This guide provides step-by-step instructions to set up and implement the testing strategy for Saules Krantas.

## Prerequisites

- Node.js 20+ installed
- npm or yarn package manager
- Git repository access
- Basic understanding of Jest and React Testing Library

---

## Step 1: Install Testing Dependencies

```bash
cd /Users/mmazuna/Projects/saules-krantas

# Install unit testing dependencies
npm install --save-dev \
  jest \
  @testing-library/react \
  @testing-library/jest-dom \
  @testing-library/user-event \
  jest-environment-jsdom \
  @types/jest \
  ts-jest

# Install E2E testing dependencies
npm install --save-dev @playwright/test

# Install additional testing utilities
npm install --save-dev \
  @axe-core/react \
  supertest \
  @types/supertest
```

---

## Step 2: Configure Jest

Create `jest.config.js` in the project root:

```javascript
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files
  dir: './',
})

// Add any custom config to be passed to Jest
const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{js,jsx,ts,tsx}',
    '!src/**/__tests__/**',
  ],
  coverageThresholds: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
}

// createJestConfig is exported this way to ensure that next/jest can load the Next.js config which is async
module.exports = createJestConfig(customJestConfig)
```

Create `jest.setup.js`:

```javascript
import '@testing-library/jest-dom'
```

---

## Step 3: Configure Playwright

Initialize Playwright:

```bash
npx playwright install
```

Create `playwright.config.ts`:

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## Step 4: Update package.json Scripts

Add these scripts to `package.json`:

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:debug": "playwright test --debug",
    "test:a11y": "pa11y http://localhost:3000",
    "test:all": "npm run test && npm run test:e2e"
  }
}
```

---

## Step 5: Create Test Directory Structure

```bash
mkdir -p __tests__/components
mkdir -p __tests__/lib
mkdir -p __tests__/api
mkdir -p e2e/public
mkdir -p e2e/admin
mkdir -p e2e/utils
```

---

## Step 6: Write Your First Tests

### Example 1: Unit Test for Auth Utility

Create `__tests__/lib/auth.test.ts`:

```typescript
import { verifyPassword, sessionOptions, defaultSession } from '@/lib/auth';

describe('auth utilities', () => {
  describe('verifyPassword', () => {
    it('should return true for correct password', () => {
      process.env.ADMIN_PASSWORD = 'test-password';
      expect(verifyPassword('test-password')).toBe(true);
    });

    it('should return false for incorrect password', () => {
      process.env.ADMIN_PASSWORD = 'test-password';
      expect(verifyPassword('wrong-password')).toBe(false);
    });
  });

  describe('sessionOptions', () => {
    it('should have correct cookie name', () => {
      expect(sessionOptions.cookieName).toBe('saules_admin_session');
    });

    it('should have httpOnly enabled', () => {
      expect(sessionOptions.cookieOptions?.httpOnly).toBe(true);
    });
  });

  describe('defaultSession', () => {
    it('should have isAuthenticated as false', () => {
      expect(defaultSession.isAuthenticated).toBe(false);
    });
  });
});
```

### Example 2: Component Test for BookingWidget

Create `__tests__/components/BookingWidget.test.tsx`:

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import BookingWidget from '@/components/BookingWidget';

const mockDictionary = {
  book_button: 'Check Availability',
  check_in: 'Check-in',
  check_out: 'Check-out',
  adults: 'Adults',
  children: 'Children',
  check_prices: 'Check Prices',
};

describe('BookingWidget', () => {
  beforeEach(() => {
    // Mock window.open
    window.open = jest.fn();
    // Mock GTM dataLayer
    (window as any).dataLayer = [];
  });

  it('renders booking form', async () => {
    render(<BookingWidget dictionary={mockDictionary} lang="en" />);
    
    await waitFor(() => {
      expect(screen.getByLabelText('Check-in date')).toBeInTheDocument();
      expect(screen.getByLabelText('Check-out date')).toBeInTheDocument();
    });
  });

  it('opens booking.com with correct parameters', async () => {
    const user = userEvent.setup();
    render(<BookingWidget dictionary={mockDictionary} lang="en" />);

    await waitFor(() => {
      const submitButton = screen.getByRole('button', { name: /check prices/i });
      expect(submitButton).toBeInTheDocument();
    });

    const submitButton = screen.getByRole('button', { name: /check prices/i });
    await user.click(submitButton);

    expect(window.open).toHaveBeenCalledWith(
      expect.stringContaining('booking.com'),
      '_blank'
    );
  });
});
```

### Example 3: API Route Test

Create `__tests__/api/admin/auth.test.ts`:

```typescript
import { POST } from '@/app/api/admin/auth/route';
import { NextRequest } from 'next/server';

describe('/api/admin/auth', () => {
  beforeEach(() => {
    process.env.ADMIN_PASSWORD = 'test-password';
    process.env.SESSION_SECRET = 'test-secret-min-32-chars-long-for-iron-session';
  });

  it('returns 400 when password is missing', async () => {
    const request = new NextRequest('http://localhost:3000/api/admin/auth', {
      method: 'POST',
      body: JSON.stringify({}),
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(400);
    expect(data.error).toBe('Password required');
  });

  it('returns 401 for invalid password', async () => {
    const request = new NextRequest('http://localhost:3000/api/admin/auth', {
      method: 'POST',
      body: JSON.stringify({ password: 'wrong-password' }),
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(401);
    expect(data.error).toBe('Invalid password');
  });
});
```

### Example 4: E2E Test for Homepage

Create `e2e/public/homepage.spec.ts`:

```typescript
import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
  test('should load homepage successfully', async ({ page }) => {
    await page.goto('/');
    
    // Check page title
    await expect(page).toHaveTitle(/Saules Krantas/i);
    
    // Check main sections are visible
    await expect(page.locator('text=Check Availability')).toBeVisible();
  });

  test('should switch languages', async ({ page }) => {
    await page.goto('/');
    
    // Click language switcher (adjust selector based on your implementation)
    await page.click('[data-testid="language-switcher"]');
    await page.click('text=English');
    
    // Verify URL changed
    await expect(page).toHaveURL(/\/en/);
  });

  test('should open booking.com with correct parameters', async ({ page, context }) => {
    await page.goto('/');
    
    // Set up listener for new page
    const [newPage] = await Promise.all([
      context.waitForEvent('page'),
      page.click('button:has-text("Check Prices")'),
    ]);

    // Verify booking.com opened
    expect(newPage.url()).toContain('booking.com');
    expect(newPage.url()).toContain('checkin=');
    expect(newPage.url()).toContain('checkout=');
  });
});
```

### Example 5: E2E Test for Admin Authentication

Create `e2e/admin/auth.spec.ts`:

```typescript
import { test, expect } from '@playwright/test';

test.describe('Admin Authentication', () => {
  test('should redirect to login when accessing admin without auth', async ({ page }) => {
    await page.goto('/admin/dashboard');
    
    // Should redirect to login
    await expect(page).toHaveURL(/\/admin\/login/);
  });

  test('should login with correct password', async ({ page }) => {
    await page.goto('/admin/login');
    
    // Fill in password (adjust selector based on your implementation)
    await page.fill('input[type="password"]', process.env.ADMIN_PASSWORD || 'test-password');
    await page.click('button:has-text("Login")');
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/\/admin\/dashboard/);
  });

  test('should logout and redirect to login', async ({ page }) => {
    // First login
    await page.goto('/admin/login');
    await page.fill('input[type="password"]', process.env.ADMIN_PASSWORD || 'test-password');
    await page.click('button:has-text("Login")');
    
    // Then logout
    await page.click('button:has-text("Logout")');
    
    // Should redirect to login
    await expect(page).toHaveURL(/\/admin\/login/);
  });
});
```

---

## Step 7: Set Up Test Environment Variables

Create `.env.test`:

```bash
NODE_ENV=test
SESSION_SECRET=test-session-secret-min-32-chars-long-for-iron-session
ADMIN_PASSWORD=test-password
NEXT_PUBLIC_GTM_ID=GTM-TEST
```

Update `jest.config.js` to load test env:

```javascript
// Add to customJestConfig
testEnvironment: 'jest-environment-jsdom',
setupFiles: ['<rootDir>/.env.test'],
```

---

## Step 8: Create Test Utilities

Create `__tests__/utils/test-helpers.ts`:

```typescript
import { render } from '@testing-library/react';
import { getDictionary } from '@/lib/dictionary';

export async function renderWithDictionary(
  component: React.ReactElement,
  lang: 'lt' | 'en' | 'ru' = 'en'
) {
  const dict = await getDictionary(lang);
  return render(component, {
    // Add any wrapper providers if needed
  });
}

export function createMockRequest(body?: any): Request {
  return new Request('http://localhost:3000/api/test', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
}
```

---

## Step 9: Run Tests

```bash
# Run unit tests
npm test

# Run unit tests in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run E2E tests (make sure dev server is running)
npm run test:e2e

# Run E2E tests in UI mode
npm run test:e2e:ui

# Run all tests
npm run test:all
```

---

## Step 10: Set Up CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: npm ci
      - run: npm test -- --coverage
      - uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run test:e2e
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

---

## Implementation Checklist

### Phase 1: Foundation (Week 1-2)
- [ ] Install all testing dependencies
- [ ] Configure Jest
- [ ] Configure Playwright
- [ ] Set up test directory structure
- [ ] Write unit tests for `lib/auth.ts`
- [ ] Write unit tests for `lib/dictionary.ts`
- [ ] Write component tests for `BookingWidget`
- [ ] Write API tests for `/api/admin/auth`
- [ ] Write API tests for `/api/admin/content`
- [ ] Write API tests for `/api/admin/facilities`
- [ ] Achieve 80%+ unit test coverage

### Phase 2: E2E Tests (Week 3-4)
- [ ] E2E test: Homepage loading
- [ ] E2E test: Language switching
- [ ] E2E test: Booking widget functionality
- [ ] E2E test: Admin authentication flow
- [ ] E2E test: Content management
- [ ] E2E test: Amenities management
- [ ] E2E test: All public pages navigation

### Phase 3: Non-Functional (Week 5-6)
- [ ] Set up accessibility testing
- [ ] Set up performance testing
- [ ] Set up security testing
- [ ] Set up visual regression testing
- [ ] Create test reports and documentation

---

## Next Steps

1. **Start with Unit Tests**: Begin with utilities and simple components
2. **Add Integration Tests**: Test API routes and middleware
3. **Implement E2E Tests**: Focus on critical user journeys first
4. **Set Up CI/CD**: Automate test execution
5. **Monitor Coverage**: Track and improve test coverage over time
6. **Refine Tests**: Continuously improve test quality and maintainability

---

## Troubleshooting

### Common Issues

**Issue**: Tests fail with "Cannot find module"
- **Solution**: Check `moduleNameMapper` in `jest.config.js` matches your `tsconfig.json` paths

**Issue**: E2E tests timeout
- **Solution**: Increase timeout in `playwright.config.ts` or check if dev server is running

**Issue**: Session tests fail
- **Solution**: Ensure `SESSION_SECRET` is set in test environment and is at least 32 characters

**Issue**: Coverage not generating
- **Solution**: Check `collectCoverageFrom` patterns in `jest.config.js`

---

## Resources

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [React Testing Library](https://testing-library.com/react)
- [Playwright Documentation](https://playwright.dev)
- [Next.js Testing Guide](https://nextjs.org/docs/testing)

---

**Last Updated**: 2025-01-27
