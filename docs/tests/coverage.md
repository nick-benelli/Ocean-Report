# Coverage Report & Analysis

Detailed code coverage analysis for the Ocean-Report test suite.

## 📊 Current Coverage: 88%

**Last Updated:** 2026-06-17  
**Total Tests:** 160  
**Measurement Tool:** pytest-cov 7.1.0

## Quick Commands

```bash
# Generate coverage report
pytest tests/ --cov=ocean_report --cov-report=html --cov-report=term-missing

# Open HTML report
open htmlcov/index.html

# Terminal report only
pytest tests/ --cov=ocean_report --cov-report=term-missing

# XML report (for CI)
pytest tests/ --cov=ocean_report --cov-report=xml
```

## Coverage by Module

### 🟢 Excellent Coverage (>90%)

| Module | Coverage | Lines | Missing | Status |
|--------|----------|-------|---------|--------|
| `api_client/client.py` | 92% | 91 | 7 | ✅ |
| `api_client/factory.py` | 100% | 6 | 0 | ✅ |
| `application/context.py` | 100% | 7 | 0 | ✅ |
| `application/factory.py` | 100% | 23 | 0 | ✅ |
| `services/tide_service.py` | 100% | 28 | 0 | ✅ |
| `services/water_temp_service.py` | 96% | 24 | 1 | ✅ |
| `services/wind_service.py` | 100% | 18 | 0 | ✅ |
| `use_cases/tides.py` | 100% | 25 | 0 | ✅ |
| `use_cases/water_temperature.py` | 96% | 24 | 1 | ✅ |
| `use_cases/wind.py` | 100% | 37 | 0 | ✅ |
| `use_cases/email.py` | 100% | 25 | 0 | ✅ |
| `workflows/data/fetcher.py` | 100% | 28 | 0 | ✅ |
| `workflows/data/formatter.py` | 100% | 8 | 0 | ✅ |
| `workflows/email/*.py` | 94-100% | Various | 2 total | ✅ |
| `workflows/report_runner.py` | 94% | 67 | 4 | ✅ |

**Analysis:** Core business logic is comprehensively tested. The few missing lines are typically error handling edge cases or debug logging.

### 🟡 Good Coverage (70-90%)

| Module | Coverage | Lines | Missing | Notes |
|--------|----------|-------|---------|-------|
| `config/loader.py` | 74% | 54 | 14 | Config edge cases |
| `config/schemas.py` | 85% | 180 | 27 | Pydantic validators |
| `emailer/email_formatter.py` | 72% | 89 | 25 | HTML formatting paths |
| `emailer/sender.py` | 87% | 60 | 8 | SMTP error paths |
| `logger.py` | 77% | 31 | 7 | Logging setup |
| `endpoints/base.py` | 84% | 31 | 5 | Base class utils |
| `utils/wind_utils.py` | 72% | 29 | 8 | Edge case angles |

**Analysis:** These modules have good coverage but could benefit from additional edge case testing. Most missing lines are:
- Exception handling branches
- Complex Pydantic validators
- HTML email formatting (less critical path)
- Logging configuration

**Recommendations:**
1. Add tests for config loading edge cases (malformed YAML, missing required fields)
2. Test email formatter with edge cases (empty data, None values)
3. Add tests for wind classification boundary angles (0°, 90°, 180°, 270°, 360°)

### 🔴 Low Coverage (<70%)

| Module | Coverage | Lines | Missing | Reason |
|--------|----------|-------|---------|--------|
| `utils/date_utils.py` | 25% | 16 | 12 | Utility functions rarely used |
| `endpoints/ndbc/base.py` | 0% | 4 | 4 | Not used in current workflow |
| `endpoints/ndbc/observations.py` | 0% | 10 | 10 | Not used in current workflow |
| `models/ndbc/*.py` | 0% | 18 | 18 | Not used in current workflow |

**Analysis:** Low coverage in these modules is acceptable because:
- **date_utils**: Helper functions for future features, not currently in use
- **NDBC modules**: Alternative data source not implemented yet

**Future Improvements:**
- When NDBC buoy data is implemented, add comprehensive service/use case tests
- If date utilities are used, add focused unit tests
- Consider removing unused code if not planned for near-term use

## Coverage Trends

| Date | Coverage | Change | Tests | Notes |
|------|----------|--------|-------|-------|
| 2026-06-17 | 88% | +34% | 160 | Added integration, performance, error quality tests |
| 2026-06-16 | 86% | +10% | 126 | Added use case and workflow tests |
| 2026-06-15 | 76% | baseline | 83 | Initial comprehensive test suite |

## Missing Coverage Analysis

### Critical Missing Lines

**api_client/client.py** (7 lines missing):
- Lines 87-88: Error handling for malformed responses
- Lines 189-190: Retry logic edge cases
- Lines 217-218: SSL verification error handling
- Line 224: Connection pool cleanup

**Recommendation:** Add tests for API client error scenarios (malformed JSON, SSL errors, connection pool exhaustion).

**config/loader.py** (14 lines missing):
- Lines 44-66: Environment variable resolution edge cases
- Line 119: Config validation error handling
- Lines 124-125: File permission errors

**Recommendation:** Add tests for:
```python
def test_config_loader_handles_missing_env_vars()
def test_config_loader_handles_invalid_yaml()
def test_config_loader_handles_file_permission_errors()
```

**emailer/email_formatter.py** (25 lines missing):
- Lines 60-63: Timestamp formatting edge cases
- Line 106: No water temperature data
- Lines 110-111: Empty tide data
- Lines 144-150: HTML table generation
- Lines 165, 186-187, 190: HTML email specific formatting
- Lines 206-221: HTML wind forecast formatting

**Recommendation:** Most missing lines are HTML email formatting (used less frequently than text). Consider:
- Adding HTML formatter tests if HTML emails are critical
- Or document that text email format is primary (current 72% coverage is acceptable)

### Non-Critical Missing Lines

These areas have low coverage but are acceptable:

1. **Debug logging statements** - Don't need test coverage
2. **Type checking branches** - Covered by Pydantic
3. **Unused feature code** (NDBC) - Will be tested when implemented
4. **Error message formatting** - Covered by error quality tests

## Coverage Configuration

Current configuration in `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["src/ocean_report"]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/site-packages/*",
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
```

## Improving Coverage

### Priority 1: Critical Paths (90% → 95%)

Add these tests to reach 95% coverage:

1. **API Client Error Handling** (~5 tests)
   ```python
   def test_api_client_handles_malformed_json()
   def test_api_client_handles_ssl_errors()
   def test_api_client_connection_pool_cleanup()
   ```

2. **Config Edge Cases** (~8 tests)
   ```python
   def test_config_loader_missing_required_fields()
   def test_config_loader_invalid_yaml_syntax()
   def test_config_loader_file_not_found()
   def test_config_loader_permission_denied()
   ```

### Priority 2: Nice to Have (95% → 98%)

3. **Email Formatter Edge Cases** (~10 tests)
   - HTML formatting with empty data
   - Timestamp formatting edge cases
   - No water temperature scenarios

4. **Wind Utils Edge Cases** (~5 tests)
   - Boundary angle classifications (0°, 360°)
   - Invalid angle handling
   - Extreme wind speeds

### Priority 3: Future Features

5. **NDBC Implementation** (when needed)
   - Service layer tests
   - Use case tests
   - Integration tests with real NDBC API

## Coverage Goals

| Goal | Current | Target | Effort |
|------|---------|--------|--------|
| **Critical paths** | 88% | 90% | Low (add 10 tests) |
| **Overall** | 88% | 90% | Medium (add 15-20 tests) |
| **All code** | 88% | 95% | High (add 30-40 tests) |

**Recommended target:** **90% coverage**

This ensures critical paths are well-tested while avoiding diminishing returns from testing rarely-used utility code.

## Coverage in CI/CD

### Current CI Coverage Check

```yaml
# .github/workflows/tests.yml
- name: Run tests with coverage
  run: |
    pytest tests/ -m "not integration" \
      --cov=ocean_report \
      --cov-report=term-missing \
      --cov-report=xml
    
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

### Coverage Badges

Add to README.md:

```markdown
[![Coverage](https://codecov.io/gh/nick-benelli/Ocean-Report/branch/main/graph/badge.svg)](https://codecov.io/gh/nick-benelli/Ocean-Report)
```

### Enforcement

To enforce minimum coverage:

```bash
# Fail if coverage drops below 85%
pytest tests/ --cov=ocean_report --cov-fail-under=85
```

## Viewing Coverage Reports

### HTML Report (Recommended)

```bash
# Generate HTML report
pytest tests/ --cov=ocean_report --cov-report=html

# Open in browser
open htmlcov/index.html
```

**Benefits:**
- Visual highlighting of covered/uncovered lines
- Interactive navigation
- Per-module drill-down
- Easy to identify missing coverage

### Terminal Report

```bash
# Quick terminal report
pytest tests/ --cov=ocean_report --cov-report=term-missing
```

**Benefits:**
- Fast feedback
- Good for CI/CD
- Shows missing line numbers

### XML Report (For Tools)

```bash
# Generate XML for external tools
pytest tests/ --cov=ocean_report --cov-report=xml
```

**Use cases:**
- Codecov/Coveralls integration
- IDE integration
- Coverage trend tracking

## Coverage Best Practices

### ✅ DO

- Focus on critical business logic first
- Test error paths and edge cases
- Aim for 80-90% coverage minimum
- Use coverage to find untested code
- Track coverage trends over time

### ❌ DON'T

- Chase 100% coverage artificially
- Test trivial getters/setters excessively
- Ignore integration test coverage
- Skip edge cases to hit target
- Add meaningless tests just for numbers

## Summary

**Current State:** 88% coverage, 160 tests  
**Status:** Excellent ✅  
**Action Items:**
1. ✅ No immediate action required
2. 📋 Consider adding API client error tests (Priority 1)
3. 📋 Consider config edge case tests (Priority 1)
4. 📋 Track coverage trends monthly

The test suite has strong coverage of critical paths and business logic. The missing coverage is primarily in edge cases, error paths, and unused features (NDBC), which is acceptable for the current state of the project.

---

**For detailed coverage data, run:**
```bash
pytest tests/ --cov=ocean_report --cov-report=html && open htmlcov/index.html
```
