# Testing Quick Reference

## 🚀 Quick Commands

```bash
# Run all tests (skip integration)
pytest tests/ -m "not integration"

# Run with coverage
pytest tests/ --cov=ocean_report --cov-report=html

# Run specific test file
pytest tests/test_workflows_fetcher.py -v

# Run specific test
pytest tests/test_end_to_end.py::test_run_report_integration_smoke_test -v
```

## 📊 Test Categories

| Category | Count | Command | Notes |
|----------|-------|---------|-------|
| **All Tests** | 160 | `pytest tests/` | Includes integration |
| **Unit Tests** | 147 | `pytest tests/ -m "not integration"` | Default for CI |
| **Integration** | 13 | `pytest tests/ -m integration` | Requires internet |
| **Performance** | 9 | `pytest tests/ -m performance` | Speed benchmarks |
| **Error Quality** | 15 | `pytest tests/ -m error_quality` | Error message tests |

## 🎯 Coverage Commands

```bash
# Quick coverage report
pytest tests/ --cov=ocean_report --cov-report=term-missing

# HTML report (detailed)
pytest tests/ --cov=ocean_report --cov-report=html
open htmlcov/index.html

# XML report (for CI)
pytest tests/ --cov=ocean_report --cov-report=xml
```

**Current Coverage:** 88%

## 🔍 Debugging

```bash
# Verbose output
pytest tests/ -v

# Show print statements
pytest tests/ -s

# Drop into debugger on failure
pytest tests/ --pdb

# Show slowest tests
pytest tests/ --durations=10
```

## ✅ Pre-Commit Checklist

```bash
# 1. Run unit tests
pytest tests/ -m "not integration" -q

# 2. Check coverage
pytest tests/ --cov=ocean_report --cov-report=term

# 3. Run performance tests
pytest tests/ -m performance -q

# 4. Optional: Run integration tests
pytest tests/ -m integration -v
```

## 📁 Test Files

```
tests/
├── Core (126 tests)
│   ├── test_end_to_end.py ⭐ Main workflow
│   ├── test_workflows_*.py ⭐ Orchestration
│   ├── test_use_cases_*.py ⭐ Business logic
│   ├── test_*_service.py ⭐ Services
│   ├── test_api_client*.py ⭐ Infrastructure
│   └── test_email_*.py ⭐ Email
├── Advanced (34 tests)
│   ├── test_integration_real_apis.py 🌐 Real APIs
│   ├── test_performance.py 🚀 Speed tests
│   └── test_error_messages.py 📝 Error quality
```

## 🏷️ Test Markers

```python
@pytest.mark.integration  # Real API calls
@pytest.mark.performance  # Speed benchmarks
@pytest.mark.benchmark    # Detailed perf tests
@pytest.mark.error_quality  # Error message tests
```

```bash
# Run by marker
pytest tests/ -m integration
pytest tests/ -m "performance or benchmark"
pytest tests/ -m "not integration"  # Default
```

## 📈 Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Total Tests | 160 | ✅ |
| Pass Rate | 100% | ✅ |
| Coverage | 88% | ✅ |
| Execution Time | ~8s (unit) | ✅ |
| Execution Time | ~30s (all) | ✅ |

## 🆘 Common Issues

**Import errors?**  
→ `pip install -e .`

**Slow tests?**  
→ `pytest tests/ -m "not integration"`

**Coverage too low?**  
→ `pytest tests/ --cov=ocean_report --cov-report=html`

**Integration tests failing?**  
→ Check internet connection and API status

## 📚 Resources

- Full guide: [docs/TESTING.md](./TESTING.md)
- pytest docs: https://docs.pytest.org/
- Coverage docs: https://pytest-cov.readthedocs.io/
