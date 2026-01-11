# Testing Checklist - Saules Krantas

Quick reference checklist for testing activities. Use this alongside the full Testing Strategy document.

## Test Setup Checklist

### Environment Setup
- [ ] Testing dependencies installed
- [ ] Jest configured
- [ ] Playwright configured
- [ ] Test environment variables set
- [ ] Test directory structure created
- [ ] CI/CD pipeline configured

---

## Unit Testing Checklist

### Utilities (`lib/`)
- [ ] `lib/auth.ts` - verifyPassword()
- [ ] `lib/auth.ts` - sessionOptions
- [ ] `lib/auth.ts` - defaultSession
- [ ] `lib/dictionary.ts` - getDictionary()
- [ ] `lib/dictionary.ts` - Language validation

### Components
- [ ] `BookingWidget` - Rendering
- [ ] `BookingWidget` - Date selection
- [ ] `BookingWidget` - Guest selection
- [ ] `BookingWidget` - Form submission
- [ ] `BookingWidget` - GTM event firing
- [ ] `Header` - Navigation
- [ ] `Header` - Language switcher
- [ ] `ApartmentCard` - Display
- [ ] `ApartmentsSection` - Filtering
- [ ] `FacilitiesSection` - Amenities display
- [ ] `Contact` - Form validation (if applicable)
- [ ] `Footer` - Links and content

### API Routes
- [ ] `/api/admin/auth` - POST with valid password
- [ ] `/api/admin/auth` - POST with invalid password
- [ ] `/api/admin/auth` - POST with missing password
- [ ] `/api/admin/logout` - POST clears session
- [ ] `/api/admin/content` - GET returns content
- [ ] `/api/admin/content` - GET with invalid language
- [ ] `/api/admin/content` - POST saves content
- [ ] `/api/admin/content` - POST validates language
- [ ] `/api/admin/facilities` - GET returns config
- [ ] `/api/admin/facilities` - PUT updates config

### Middleware
- [ ] Redirects unauthenticated users to login
- [ ] Allows access to login page
- [ ] Protects admin routes
- [ ] Session validation works

---

## Integration Testing Checklist

### API Integration
- [ ] Auth API with session creation
- [ ] Content API with file system operations
- [ ] Facilities API with state persistence
- [ ] Error handling for all endpoints
- [ ] Request validation

### Component Integration
- [ ] BookingWidget with date validation
- [ ] Language switching updates all components
- [ ] Admin panel content editing flow
- [ ] Amenities toggle updates UI

---

## E2E Testing Checklist

### Public Pages
- [ ] Homepage loads successfully
- [ ] All sections render correctly
- [ ] Language switching (LT → EN → RU)
- [ ] Language persistence in URL
- [ ] Navigation links work
- [ ] Footer links work
- [ ] Responsive design (mobile/tablet/desktop)

### Booking Widget
- [ ] Date picker works
- [ ] Check-out date validation (after check-in)
- [ ] Guest selection works
- [ ] Submit button disabled when invalid
- [ ] Redirects to booking.com with params
- [ ] GTM event fires

### Admin Panel
- [ ] Unauthenticated access redirects to login
- [ ] Login with correct password
- [ ] Login with incorrect password
- [ ] Session persists after login
- [ ] Logout clears session
- [ ] Dashboard displays correctly
- [ ] Content management page loads
- [ ] Amenities management page loads

### Content Management
- [ ] Load content for each language
- [ ] Edit content and save
- [ ] Changes persist
- [ ] Invalid data rejected
- [ ] File system errors handled

### Amenities Management
- [ ] Load current state
- [ ] Toggle amenities on/off
- [ ] Save changes
- [ ] UI updates reflect changes

---

## Accessibility Testing Checklist

### WCAG 2.1 AA Compliance
- [ ] All images have alt text
- [ ] All form inputs have labels
- [ ] Color contrast meets 4.5:1 ratio
- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] Screen reader compatibility
- [ ] No keyboard traps
- [ ] Heading hierarchy correct
- [ ] Links have descriptive text
- [ ] Error messages accessible
- [ ] Skip navigation links (if applicable)
- [ ] ARIA labels where needed

### Tools Used
- [ ] axe-core automated scan
- [ ] Pa11y CLI scan
- [ ] Lighthouse accessibility audit
- [ ] Manual screen reader testing (NVDA/JAWS/VoiceOver)
- [ ] Keyboard-only navigation test

---

## Performance Testing Checklist

### Core Web Vitals
- [ ] LCP < 2.5s
- [ ] FID < 100ms
- [ ] CLS < 0.1
- [ ] TTFB < 600ms
- [ ] FCP < 1.8s

### Page Load Times
- [ ] Homepage < 3s
- [ ] Admin pages < 2s
- [ ] API responses < 500ms

### Optimization
- [ ] Images optimized
- [ ] JavaScript bundle size acceptable
- [ ] Font loading optimized
- [ ] CSS minified
- [ ] Caching headers set

### Tools Used
- [ ] Lighthouse CI
- [ ] WebPageTest
- [ ] Chrome DevTools Performance
- [ ] Next.js Analytics

---

## Security Testing Checklist

### Authentication
- [ ] Password validation works
- [ ] Brute force protection (rate limiting)
- [ ] Session timeout enforced
- [ ] Secure cookie flags (httpOnly, secure)
- [ ] Session fixation prevention

### Input Validation
- [ ] XSS prevention in content fields
- [ ] Path traversal prevention
- [ ] Invalid language parameters rejected
- [ ] Malformed JSON handled
- [ ] Oversized payloads rejected

### Authorization
- [ ] Unauthenticated API access blocked
- [ ] Direct admin route access blocked
- [ ] Session validation on all protected routes

### Dependencies
- [ ] npm audit run (no critical vulnerabilities)
- [ ] Snyk scan (if configured)
- [ ] Environment variables secured

---

## Internationalization Testing Checklist

### Language Support
- [ ] Lithuanian (LT) - All content
- [ ] English (EN) - All content
- [ ] Russian (RU) - All content

### Language Switching
- [ ] Switch from LT to EN
- [ ] Switch from EN to RU
- [ ] Switch from RU to LT
- [ ] Language persists in URL
- [ ] All components update

### Content Validation
- [ ] No missing translations
- [ ] Date formats per locale
- [ ] Number formats per locale
- [ ] Text overflow handled
- [ ] RTL support (if applicable)

### URL Structure
- [ ] Language codes in URLs work
- [ ] Default language redirects
- [ ] Invalid language codes handled

---

## SEO Testing Checklist

### Meta Tags
- [ ] Title tags present and unique
- [ ] Meta descriptions present
- [ ] Open Graph tags
- [ ] Twitter Card tags

### Structured Data
- [ ] JSON-LD present
- [ ] Schema.org validation passes
- [ ] Business information correct

### Technical SEO
- [ ] Sitemap.xml generated
- [ ] Robots.txt configured
- [ ] Canonical URLs set
- [ ] Hreflang tags (if applicable)
- [ ] 404 page exists
- [ ] Redirects work correctly

### Tools Used
- [ ] Google Search Console
- [ ] Schema.org validator
- [ ] Screaming Frog (if available)

---

## Cross-Browser Testing Checklist

### Desktop Browsers
- [ ] Chrome (latest 2 versions)
- [ ] Firefox (latest 2 versions)
- [ ] Safari (latest 2 versions)
- [ ] Edge (latest 2 versions)

### Mobile Browsers
- [ ] iOS Safari
- [ ] Chrome Mobile
- [ ] Samsung Internet (if applicable)

### Test Areas
- [ ] Layout rendering
- [ ] JavaScript functionality
- [ ] Form inputs
- [ ] Date pickers
- [ ] Responsive design

---

## Visual Regression Testing Checklist

### Pages to Test
- [ ] Homepage (all languages)
- [ ] Admin dashboard
- [ ] Admin content page
- [ ] Admin amenities page

### Breakpoints
- [ ] Mobile (375px)
- [ ] Tablet (768px)
- [ ] Desktop (1920px)

### Components
- [ ] BookingWidget
- [ ] ApartmentCard
- [ ] Header
- [ ] Footer

---

## Test Execution Status

### Test Runs
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Accessibility tests passing
- [ ] Performance tests passing
- [ ] Security tests passing

### Coverage
- [ ] Unit test coverage ≥ 80%
- [ ] API endpoint coverage 100%
- [ ] Critical user journeys 100%

### Documentation
- [ ] Test results documented
- [ ] Bugs logged and tracked
- [ ] Test reports generated
- [ ] Coverage reports generated

---

## Pre-Release Checklist

### Quality Gates
- [ ] All critical bugs fixed
- [ ] All tests passing
- [ ] Coverage targets met
- [ ] Performance benchmarks met
- [ ] Accessibility compliance verified
- [ ] Security scan passed
- [ ] Cross-browser testing completed
- [ ] Stakeholder sign-off received

### Final Checks
- [ ] Production environment variables set
- [ ] Error monitoring configured
- [ ] Analytics tracking verified
- [ ] Backup strategy in place
- [ ] Rollback plan documented

---

## Notes

- Update this checklist as new features are added
- Mark items as complete with date and tester initials
- Escalate blockers immediately
- Document any deviations from the plan

---

**Last Updated**: 2025-01-27
