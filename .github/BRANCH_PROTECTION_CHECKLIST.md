# Branch Protection Checklist

Use this checklist to verify branch protection is correctly configured on GitHub.

## Required Settings for `main` Branch

### ✅ Basic Protection
- [ ] **Protect this branch**: Enabled
- [ ] **Require a pull request before merging**: Enabled
  - [ ] Require approvals: **1** (or more if you prefer)
  - [ ] Dismiss stale pull request approvals when new commits are pushed: **Enabled**
  - [ ] Require review from Code Owners: Optional (if you have CODEOWNERS file)

### ✅ Status Checks
- [ ] **Require status checks to pass before merging**: Enabled
- [ ] **Require branches to be up to date before merging**: Enabled
- [ ] **Required status checks** (select these):
  - [ ] `lint` (from test.yml workflow)
  - [ ] `python-tests (3.11)` (from test.yml workflow)
  - [ ] `frontend-tests` (from test.yml workflow)
  - [ ] `build` (from build.yml workflow) - Optional but recommended

### ✅ Additional Rules
- [ ] **Require conversation resolution before merging**: Recommended
- [ ] **Require linear history**: Optional (prevents merge commits)
- [ ] **Include administrators**: Optional (if you want admins to bypass rules)

### ✅ Restrict Who Can Push
- [ ] **Restrict pushes that create matching branches**: Optional
- [ ] **Allow force pushes**: **Disabled** (security)
- [ ] **Allow deletions**: **Disabled** (security)

## How to Configure

1. Go to: **Settings** → **Branches**
2. Click **Add rule** or edit existing rule for `main`
3. Configure the settings above
4. Click **Save changes**

## Verification

After configuring, test by:
1. Creating a test branch
2. Making a change
3. Opening a PR
4. Verifying that:
   - PR cannot be merged until tests pass
   - Required reviewers must approve
   - Status checks are visible and required

## Current Workflow Status Checks

The following status checks should be available:
- `lint` - Code linting
- `python-tests (3.9)` - Python tests on 3.9
- `python-tests (3.10)` - Python tests on 3.10
- `python-tests (3.11)` - Python tests on 3.11 (recommended to require)
- `frontend-tests` - Frontend tests
- `build` - Build validation
- `test-summary` - Test summary (optional)

**Recommended minimum**: Require `python-tests (3.11)` and `frontend-tests`

---

**Last Updated**: 2025-01-27
