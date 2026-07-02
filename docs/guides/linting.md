# Linting and Code Quality Guide

This project uses **Ruff** for fast, modern Python linting and formatting, along with **mypy** for type checking.

## 🚀 Quick Start

### Install Development Dependencies

```bash
uv pip install -e ".[dev]"
```

### Run Linting

```bash
# Check for linting issues
uv run ruff check .

# Auto-fix issues
uv run ruff check . --fix

# Format code
uv run ruff format .
```

### Run Type Checking

```bash
uv run mypy src/ocean_report
```

## 🪝 Pre-commit Hooks

Pre-commit hooks automatically run linting and formatting before each commit.

### Setup

```bash
pip install pre-commit
pre-commit install
```

### Usage

Pre-commit hooks run automatically on `git commit`. To run manually:

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run
```

### Skip Hooks (Emergency Only)

```bash
git commit --no-verify
```

## 🔧 Configuration

### Ruff Configuration

Located in [`pyproject.toml`](../../pyproject.toml):

- **Target**: Python 3.12+
- **Line length**: 100 characters
- **Rules enabled**:
  - `E/W`: pycodestyle errors and warnings
  - `F`: pyflakes
  - `I`: isort (import sorting)
  - `B`: flake8-bugbear
  - `C4`: flake8-comprehensions
  - `UP`: pyupgrade (modern Python syntax)
  - `ARG`: unused arguments
  - `SIM`: code simplification

### Pre-commit Hooks

Located in [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml):

1. **Standard checks**: trailing whitespace, file endings, YAML/JSON validation
2. **Ruff**: linting and formatting
3. **mypy**: type checking

## 🔄 CI/CD Integration

GitHub Actions automatically runs linting and tests on:
- Push to `main`, `remodel`, or `feature/*` branches
- Pull requests to `main`

See [`.github/workflows/tests.yml`](../../.github/workflows/tests.yml) for details.

The CI workflow includes:
1. **Lint job**: Runs ruff check and format verification
2. **Test job**: Runs pytest with coverage (minimum 85%)

## 📊 Current Status

After initial setup (as of 2026-07-02):

- ✅ **115 issues auto-fixed** by ruff
- ✅ **35 files reformatted**
- ⚠️ **20 minor issues remaining** (mostly unused test variables)
- ✅ **All tests passing** (153 tests)
- ✅ **88% test coverage**

### Remaining Issues

The 20 remaining linting issues are minor and mostly in tests:

- 9 unused variables in tests (F841)
- 6 blank lines with whitespace (W293)
- 2 overly broad exception assertions (B017)
- 1 missing `strict=` in `zip()` (B905)
- 1 useless comparison in notebook (B015)
- 1 `!= False` comparison (E712)

These can be addressed gradually without blocking development.

## 🛠️ IDE Integration

### VS Code

Install the Ruff extension:

```bash
code --install-extension charliermarsh.ruff
```

Add to `.vscode/settings.json`:

```json
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "explicit",
      "source.organizeImports.ruff": "explicit"
    }
  }
}
```

### PyCharm

1. Install the **Ruff** plugin from the marketplace
2. Configure it in Settings → Tools → Ruff
3. Enable "Run on save" for automatic formatting

## 📚 Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Ruff Rules Reference](https://docs.astral.sh/ruff/rules/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [mypy Documentation](https://mypy.readthedocs.io/)

## 🎯 Best Practices

1. **Run linting locally** before pushing
2. **Use pre-commit hooks** to catch issues early
3. **Fix issues incrementally** - don't let them accumulate
4. **Use `--fix` flag** for auto-fixable issues
5. **Review formatting changes** before committing
6. **Keep configuration updated** as Ruff evolves

---

*For questions or issues, see the main [README](../../README.md) or open an issue.*
