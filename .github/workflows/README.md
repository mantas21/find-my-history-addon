# CI/CD Workflows

This directory contains GitHub Actions workflows for continuous integration and deployment.

## Workflows

### 1. `test.yml` - Comprehensive Testing
**Triggers**: Push to main/develop, Pull Requests, Manual dispatch

**Jobs**:
- **lint**: Code quality checks (pylint, black, mypy)
- **python-tests**: Python tests across multiple versions (3.9, 3.10, 3.11)
- **frontend-tests**: JavaScript/Node.js tests
- **test-summary**: Aggregates test results

**Features**:
- Parallel test execution
- Coverage reporting to Codecov
- Artifact uploads
- Coverage threshold enforcement

### 2. `ci.yml` - Quick CI Checks
**Triggers**: Pull Requests, Push to main/develop

**Jobs**:
- **quick-check**: Fast validation (syntax, JSON, structure)
- **full-tests**: Complete test suite (runs after quick-check passes)

**Features**:
- Fast feedback for PRs
- Concurrency control (cancels previous runs)
- Timeout protection

### 3. `build.yml` - Build Validation
**Triggers**: Push to main, Tags, Pull Requests, Manual dispatch

**Jobs**:
- **build**: Validates add-on structure and configuration

**Features**:
- Config.json validation
- Dockerfile validation
- Structure validation

### 4. `release.yml` - Release Management
**Triggers**: Version tags (v*.*.*), Manual dispatch

**Jobs**:
- **release**: Creates GitHub releases

**Features**:
- Automatic changelog extraction
- Release notes generation
- Draft/prerelease support

## Workflow Status

You can check workflow status at:
- https://github.com/[owner]/[repo]/actions

## Badges

Add these badges to your README:

```markdown
![Tests](https://github.com/[owner]/[repo]/workflows/Tests/badge.svg)
![CI](https://github.com/[owner]/[repo]/workflows/CI/badge.svg)
![Build](https://github.com/[owner]/[repo]/workflows/Build/badge.svg)
```

## Local Testing

Before pushing, test locally:

```bash
# Run all tests
pytest tests/ -v

# Run frontend tests
cd tests/frontend && npm test

# Check linting
pylint find_my_history_addon/find_my_history/
black --check find_my_history_addon/ tests/
```

## Secrets

No secrets required for basic workflows. For advanced features:
- `GITHUB_TOKEN`: Automatically provided
- Codecov token: Optional (for private repos)

## Troubleshooting

### Tests failing in CI but passing locally
- Check Python version matches
- Verify all dependencies are in requirements.txt
- Check for environment-specific issues

### Coverage threshold failures
- Current threshold: 45% (adjusted for realistic coverage)
- Increase coverage or adjust threshold in workflow

### Frontend tests failing
- Ensure Node.js version matches (v20)
- Check npm cache is working
- Verify package-lock.json is committed
