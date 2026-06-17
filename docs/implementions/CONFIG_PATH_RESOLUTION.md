# Config Path Resolution Guide

## Overview

Ocean Report now uses production-ready config path resolution with environment variable support and sensible fallbacks.

## Resolution Order

The app searches for `config.yaml` in this order:

1. **`OCEAN_REPORT_CONFIG` environment variable** (highest priority)
   - Explicit path override
   - Use this in custom deployments, Docker, or cloud environments

2. **Project-relative path** (default for development & GitHub Actions)
   - `configs/config.yaml` relative to `pyproject.toml`
   - Works automatically when you check out the repo

3. **User config directory** (installed package fallback)
   - `~/.config/ocean-report/config.yaml`
   - Standard location for installed CLI tools

4. **Error with helpful message** if no config found

## Usage Examples

### Local Development (Default)
No configuration needed! Just run:
```bash
uv run scripts/run_report_no_email.py
```
Uses `configs/config.yaml` from the repo.

### GitHub Actions (Default)
No changes needed! Your workflows already work because:
- Repo is checked out with `actions/checkout@v4`
- Config file at `configs/config.yaml` is automatically found

### Custom Config Path
Set the environment variable:

```bash
# One-time use
OCEAN_REPORT_CONFIG=/path/to/custom-config.yaml uv run scripts/run_report.py

# In .env file (for persistent local override)
OCEAN_REPORT_CONFIG=/Users/me/my-custom-config.yaml

# In Docker/cloud
docker run -e OCEAN_REPORT_CONFIG=/app/config.yaml ocean-report
```

### Installed Package
If you install Ocean Report as a package (`pip install .`), place your config at:
```
~/.config/ocean-report/config.yaml
```

## GitHub Actions Setup

Your existing workflows already work! But if you need to use a different config:

```yaml
- name: Run water report
  env:
    # Optional: override config location
    OCEAN_REPORT_CONFIG: /path/to/config.yaml
    
    # Your existing secrets
    EMAIL_SENDER: ${{ secrets.EMAIL_SENDER }}
    # ... rest of your env vars
  run: python scripts/run_report.py
```

## Benefits

✅ **Works everywhere**: Local, CI/CD, Docker, Kubernetes, cloud functions  
✅ **Zero config for common case**: Repo checkouts work automatically  
✅ **Explicit override**: Set `OCEAN_REPORT_CONFIG` when needed  
✅ **Clear errors**: Helpful message if config not found  
✅ **Standard practice**: Follows 12-factor app principles  

## Migration from Old System

**No migration needed!** If you were running from the repo root, everything works exactly the same.

The old `constants.py` file has been removed because:
- It was only used for config path resolution
- Path resolution is now self-contained in `config/loader.py`
- Environment variable support is more flexible

## Troubleshooting

### "No config file found" error

The app will show you exactly where it looked:
```
FileNotFoundError: No config file found. Tried:
  - OCEAN_REPORT_CONFIG env var
  - /path/to/repo/configs/config.yaml
  - ~/.config/ocean-report/config.yaml
Set OCEAN_REPORT_CONFIG=/path/to/config.yaml or place config in one of the above locations.
```

**Solution**: Either:
1. Run from the repo root (where `pyproject.toml` exists)
2. Set `OCEAN_REPORT_CONFIG` to point to your config
3. Copy config to `~/.config/ocean-report/config.yaml`

### Using in Docker

```dockerfile
# Copy config into image
COPY configs/config.yaml /app/config.yaml

# Set env var
ENV OCEAN_REPORT_CONFIG=/app/config.yaml

# Or rely on default if you copy the whole repo
WORKDIR /app
COPY . .
# config.yaml will be found automatically at configs/config.yaml
```

## Technical Details

- Implementation: `src/ocean_report/config/loader.py`
- Uses `find_dotenv("pyproject.toml")` to locate project root
- Paths are resolved with `pathlib.Path` for cross-platform compatibility
- `~` expansion supported for home directory paths
