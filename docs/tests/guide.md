# Testing Guide

Comprehensive guide to the Ocean-Report test suite.

## Quick Start

```bash
# Run all tests (exclude integration tests with real APIs)
pytest tests/ -m "not integration"

# Run all tests including integration (requires internet)
pytest tests/

# Run with coverage report
pytest tests/ --cov=ocean_report --cov-report=html --cov-report=term-missing

# Run specific test categories
pytest tests/ -m performance
pytest tests/ -m error_quality
pytest tests/ -m integration
```

## Test Suite Overview

**Total Tests:** 150 tests  
**Current Coverage:** 88%  
**Test Execution Time:** ~8 seconds (without integration tests)

### Test Categories

#### 1. **Unit Tests** (126 tests)
Standard mock-based unit tests covering all layers:

- **Infrastructure** (46 tests): API client, factories, configuration
- **Business Logic** (34 tests): Services, use cases
- **Workflows** (27 tests): Orchestration, data fetching, formatting, email
- **Email** (13 tests): Formatting, sending
- **Utilities** (6 tests): Wind, date utils, models

```bash
# Run unit tests only
pytest tests/ -m "not integration and not performance and not error_quality"
```

#### 2. **Integration Tests** (13 tests)
Real API tests with external services (NOAA, OpenMeteo):

```bash
# Run integration tests (requires internet)
pytest tests/test_integration_real_apis.py -m integration -v
```

**Tests include:**
- Tide service with real NOAA API
- Water temperature service with real NOAA API  
- Wind service with real OpenMeteo API
- Use case layer integration
- End-to-end workflow with real APIs
- Error handling with invalid stations
- API response time validation

**⚠️ Note:** Integration tests make real HTTP requests and may fail if:
- No internet connection
- External APIs are down
- Rate limits are exceeded

#### 3. **Performance Tests** (9 tests)
Verify critical operations complete within time limits:

```bash
# Run performance tests
pytest tests/test_performance.py -m performance -v
```

**Performance Benchmarks:**
- `fetch_raw_data`: < 100ms (mocked)
- `format_report_data`: < 50ms (large dataset)
- `format_tide_for_email`: < 100ms (96 events)
- `classify_wind_relative_to_beach`: < 10ms (72 classifications)
- `generate_email_body`: < 10ms
- `load_app_config`: < 100ms
- `create_application_context`: < 200ms
- Pydantic validation: < 50ms (100 records)
- Full workflow: < 150ms

#### 4. **Error Message Quality Tests** (15 tests)
Verify error messages are helpful and actionable:

```bash
# Run error quality tests
pytest tests/test_error_messages.py -m error_quality -v
```

**Tests verify:**
- API errors include endpoint URLs
- Timeout errors are clear
- HTTP errors include context
- Service errors mention relevant IDs
- Config errors are helpful
- Pydantic validation errors are readable
- Error messages avoid jargon
- Multiple validation errors are listed

## Test Markers

Defined in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "integration: marks tests as integration tests (may require external services)",
    "performance: marks tests as performance/speed tests",
    "benchmark: marks tests as detailed performance benchmarks",
    "error_quality: marks tests that verify error message quality",
]
```

### Running Tests by Marker

```bash
# Skip integration tests (default for CI)
pytest tests/ -m "not integration"

# Run only fast tests (unit + performance)
pytest tests/ -m "not integration" --durations=10

# Run only integration tests
pytest tests/ -m integration

# Run performance benchmarks
pytest tests/ -m "performance or benchmark"

# Run error quality tests
pytest tests/ -m error_quality
```

## Coverage Reporting

### Generate Coverage Report

```bash
# Terminal report with missing lines
pytest tests/ --cov=ocean_report --cov-report=term-missing

# HTML report (opens in browser)
pytest tests/ --cov=ocean_report --cov-report=html
open htmlcov/index.html
```

### Coverage Configuration

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
```

### Current Coverage (88%)

**High Coverage (>90%):**
- API client (92%)
- Application context (100%)
- Factories (100%)
- Services (96-100%)
- Use cases (96-100%)
- Workflows (94-100%)
- Email operations (87%)

**Medium Coverage (70-90%):**
- Config loader (74%)
- Email formatter (72%)
- Wind utils (72%)
- Logger (77%)
- Base endpoints (84%)

**Low Coverage (<70%):**
- Date utils (25%) - utility functions not heavily used
- NDBC modules (0%) - not used in current workflow

## Test File Structure

```
tests/
├── test_api_client.py                    # 9 tests - HTTP client
├── test_api_client_factory.py            # 12 tests - Client creation
├── test_application_context_factory.py   # 22 tests - Context creation
├── test_config.py                        # 3 tests - Configuration
├── test_email_formatter.py               # 9 tests - Email formatting
├── test_email_sender.py                  # 4 tests - SMTP sending
├── test_end_to_end.py                    # 7 tests - Main entry point
├── test_endpoints_stations.py            # 1 test - NOAA stations
├── test_endpoints_water_temperature.py   # 2 tests - Water temp endpoint
├── test_gist_url.py                      # 4 tests - Recipient fetching
├── test_models_noaa_water_temperature.py # 3 tests - Data models
├── test_tide_service.py                  # 3 tests - Tide service
├── test_water_temp_service.py            # 3 tests - Water temp service
├── test_wind_service.py                  # 2 tests - Wind service
├── test_wind.py                          # 2 tests - Wind utils
├── test_use_cases_tides.py               # 5 tests - Tide use case
├── test_use_cases_water_temperature.py   # 4 tests - Water temp use case
├── test_use_cases_wind.py                # 6 tests - Wind use case
├── test_use_cases_email.py               # 5 tests - Email use case
├── test_workflows_fetcher.py             # 5 tests - Data fetching
├── test_workflows_formatter.py           # 5 tests - Data formatting
├── test_workflows_email.py               # 10 tests - Email workflow
├── test_integration_real_apis.py         # 13 tests ⚠️ Real APIs
├── test_performance.py                   # 9 tests 🚀 Speed tests
└── test_error_messages.py                # 15 tests 📝 Error quality
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install -e .
      - run: pytest tests/ -m "not integration" --cov=ocean_report
```

**Default CI behavior:**
- Skip integration tests (no external API calls)
- Run unit, performance, and error quality tests
- Generate coverage report
- Fail if tests don't pass

### Optional: Run Integration Tests in CI

```yaml
# Add to workflow for scheduled runs
- name: Integration Tests
  if: github.event_name == 'schedule'
  run: pytest tests/ -m integration
```

## Writing New Tests

### Test Structure

```python
"""Module docstring explaining test purpose."""

import pytest
from unittest.mock import Mock, patch

# Import what you're testing
from ocean_report.services import tide_service
from ocean_report.models.noaa.tides import NoaaTideParams


@pytest.fixture
def mock_context():
    """Create a mock application context."""
    config = AppConfig()
    return ApplicationContext(config=config, client=Mock())


def test_descriptive_name(mock_context):
    """Test docstring explaining what this verifies."""
    # Arrange
    params = NoaaTideParams(
        station="8534720",
        begin_date="20250704",
        end_date="20250704"
    )
    
    # Act
    result = tide_service.fetch_tide_data(
        context=mock_context,
        params=params
    )
    
    # Assert
    assert result is not None
    assert len(result) > 0
```

### Best Practices

1. **Use descriptive test names** - `test_what_it_does_under_condition`
2. **One assertion per test** (when possible)
3. **Arrange-Act-Assert pattern**
4. **Mock external dependencies** (HTTP, file I/O, time)
5. **Use fixtures** for common setup
6. **Add docstrings** to explain complex tests
7. **Mark tests appropriately** (`@pytest.mark.integration`, etc.)

### Adding Integration Tests

```python
@pytest.mark.integration
def test_real_api_call(context):
    """Test with real external API."""
    # This test makes actual HTTP requests
    result = fetch_data_from_api(context)
    assert result is not None
```

### Adding Performance Tests

```python
@pytest.mark.performance
def test_operation_speed():
    """Test that operation completes quickly."""
    import time
    
    start = time.time()
    perform_operation()
    elapsed = time.time() - start
    
    assert elapsed < 0.1, f"Took {elapsed*1000:.2f}ms (expected <100ms)"
```

## Debugging Tests

### Run specific test
```bash
pytest tests/test_file.py::test_specific_function -v
```

### Show print statements
```bash
pytest tests/ -s
```

### Drop into debugger on failure
```bash
pytest tests/ --pdb
```

### Show locals on failure
```bash
pytest tests/ -l
```

### Verbose output with traceback
```bash
pytest tests/ -vv --tb=long
```

## Common Issues

### Issue: Integration tests failing
**Solution:** Check internet connection and external API status

### Issue: Performance tests failing
**Solution:** May be slower on CI or older machines - adjust thresholds if needed

### Issue: Import errors
**Solution:** Install package in development mode: `pip install -e .`

### Issue: Coverage too low
**Solution:** Identify uncovered code with `--cov-report=html` and add tests

## Test Maintenance

### When to Update Tests

- **Code changes**: Update tests to match new behavior
- **New features**: Add tests for new functionality
- **Bug fixes**: Add regression test before fixing
- **Refactoring**: Ensure tests still pass
- **API changes**: Update integration tests

### Test Health Checklist

✅ All tests pass  
✅ Coverage above 85%  
✅ No skipped tests  
✅ No warnings  
✅ Fast execution (<30s total)  
✅ Integration tests pass (optional)  
✅ Performance benchmarks met  

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Pydantic Testing](https://docs.pydantic.dev/latest/concepts/validation/)
