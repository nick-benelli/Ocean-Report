# Configuration Setup Guide

## Overview

Ocean Report uses production-ready config path resolution with environment variable support and sensible fallbacks. The configuration system is built for flexibility across different deployment environments while being zero-config for local development.

---

## Config Path Resolution

The app searches for `config.yaml` in this order:

### 1. `OCEAN_REPORT_CONFIG` Environment Variable (Highest Priority)

Explicit path override for custom deployments.

**Use when:**
- Custom deployments
- Docker containers
- Cloud environments (AWS Lambda, Azure Functions, etc.)
- CI/CD pipelines with specific config files

**Example:**
```bash
OCEAN_REPORT_CONFIG=/path/to/custom-config.yaml uv run scripts/run_report.py
```

---

### 2. Project-Relative Path (Default)

`configs/config.yaml` relative to `pyproject.toml`

**Use when:**
- Local development
- GitHub Actions
- Running from repo checkout

**Benefits:**
- Works automatically with no configuration
- Standard location in repo
- Easy to find and edit

**Example:**
```bash
# Just works - no env vars needed!
uv run scripts/run_report_no_email.py
```

---

### 3. User Config Directory (Installed Package Fallback)

`~/.config/ocean-report/config.yaml`

**Use when:**
- Ocean Report is installed as a package (`pip install .`)
- Running as a system service
- User-specific configuration

**Standard Location:**
- Linux/macOS: `~/.config/ocean-report/config.yaml`
- Follows XDG Base Directory Specification

---

### 4. Error with Helpful Message

If no config found, you get a clear error message:

```
FileNotFoundError: No config file found. Tried:
  - OCEAN_REPORT_CONFIG env var
  - /path/to/repo/configs/config.yaml
  - ~/.config/ocean-report/config.yaml

Set OCEAN_REPORT_CONFIG=/path/to/config.yaml or place config in one of the above locations.
```

---

## Usage Examples

### Local Development (Default - No Setup Required)

```bash
# Just works!
uv run scripts/run_report_no_email.py
```

Uses `configs/config.yaml` from the repo automatically.

---

### GitHub Actions (Default - No Setup Required)

Your workflows already work because:
- Repo is checked out with `actions/checkout@v4`
- Config file at `configs/config.yaml` is automatically found

```yaml
- name: Checkout code
  uses: actions/checkout@v4

- name: Run report
  run: python scripts/run_report.py
  # No OCEAN_REPORT_CONFIG needed!
```

---

### Custom Config Path (One-Time Override)

```bash
# One-time use
OCEAN_REPORT_CONFIG=/path/to/custom-config.yaml uv run scripts/run_report.py
```

---

### Custom Config Path (Persistent via .env)

```bash
# In .env file
OCEAN_REPORT_CONFIG=/Users/me/my-custom-config.yaml
```

Then just run normally:
```bash
uv run scripts/run_report.py
```

---

### Docker Deployment

**Option 1: Copy entire repo**
```dockerfile
WORKDIR /app
COPY . .
# config.yaml found automatically at configs/config.yaml
CMD ["python", "scripts/run_report.py"]
```

**Option 2: Explicit config path**
```dockerfile
COPY configs/config.yaml /app/config.yaml
ENV OCEAN_REPORT_CONFIG=/app/config.yaml
CMD ["python", "scripts/run_report.py"]
```

---

### Kubernetes Deployment

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ocean-report-config
data:
  config.yaml: |
    # Your config here...
---
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: ocean-report
        env:
        - name: OCEAN_REPORT_CONFIG
          value: /etc/ocean-report/config.yaml
        volumeMounts:
        - name: config
          mountPath: /etc/ocean-report
      volumes:
      - name: config
        configMap:
          name: ocean-report-config
```

---

### Multiple Environment Configs

```bash
# Development
OCEAN_REPORT_CONFIG=configs/dev.yaml uv run scripts/run_report.py

# Staging
OCEAN_REPORT_CONFIG=configs/staging.yaml uv run scripts/run_report.py

# Production
OCEAN_REPORT_CONFIG=configs/prod.yaml uv run scripts/run_report.py
```

Or create a helper script:
```bash
#!/bin/bash
# scripts/run_for_env.sh
ENV=${1:-dev}
OCEAN_REPORT_CONFIG="configs/${ENV}.yaml" uv run scripts/run_report.py
```

Usage:
```bash
./scripts/run_for_env.sh dev
./scripts/run_for_env.sh prod
```

---

## Benefits

✅ **Works everywhere:** Local, CI/CD, Docker, Kubernetes, cloud functions  
✅ **Zero config for common case:** Repo checkouts work automatically  
✅ **Explicit override:** Set `OCEAN_REPORT_CONFIG` when needed  
✅ **Clear errors:** Helpful message if config not found  
✅ **Standard practice:** Follows 12-factor app principles  
✅ **Cross-platform:** Works on Linux, macOS, Windows

---

## Configuration Loading Architecture

### Path Resolution Flow

```
resolve_config_path(path) called
         ↓
   path provided?
    ├─ Yes → Resolve to absolute Path
    └─ No  ↓
         ↓
   OCEAN_REPORT_CONFIG set?
    ├─ Yes → Use env var value
    └─ No  ↓
         ↓
   Find project root (pyproject.toml)
    ├─ Found → Use configs/config.yaml
    └─ Not found ↓
         ↓
   Use ~/.config/ocean-report/config.yaml
```

### Loading Pipeline

```
resolve_config_path()  →  Determines which file to load
         ↓
load_raw_config()      →  Loads YAML + substitutes ${VAR}
         ↓
load_app_config()      →  Validates with Pydantic schemas
         ↓
get_settings()         →  Caches for performance (production)
```

---

## Troubleshooting

### Error: "No config file found"

**Symptom:**
```
FileNotFoundError: No config file found. Tried:
  - OCEAN_REPORT_CONFIG env var
  - /path/to/repo/configs/config.yaml
  - ~/.config/ocean-report/config.yaml
```

**Solutions:**

1. **Run from repo root** (where `pyproject.toml` exists)
   ```bash
   cd /path/to/Ocean-Report
   uv run scripts/run_report.py
   ```

2. **Set `OCEAN_REPORT_CONFIG`** to point to your config
   ```bash
   OCEAN_REPORT_CONFIG=/absolute/path/to/config.yaml uv run scripts/run_report.py
   ```

3. **Copy config to user directory**
   ```bash
   mkdir -p ~/.config/ocean-report
   cp configs/config.yaml ~/.config/ocean-report/
   ```

---

### Error: Config file exists but not found

**Cause:** Running from wrong directory

**Solution:** Either:
- Run from repo root
- Use absolute path in `OCEAN_REPORT_CONFIG`

```bash
# ❌ Wrong - relative path from wrong directory
cd /tmp
uv run /path/to/Ocean-Report/scripts/run_report.py

# ✅ Right - run from repo root
cd /path/to/Ocean-Report
uv run scripts/run_report.py

# ✅ Right - absolute path
OCEAN_REPORT_CONFIG=/path/to/Ocean-Report/configs/config.yaml \
  uv run /path/to/Ocean-Report/scripts/run_report.py
```

---

### Using in GitHub Actions with Custom Config

```yaml
- name: Setup custom config
  run: |
    echo "Creating custom config..."
    cp configs/config.yaml configs/custom.yaml
    # Make modifications to custom.yaml

- name: Run with custom config
  env:
    OCEAN_REPORT_CONFIG: configs/custom.yaml
    EMAIL_SENDER: ${{ secrets.EMAIL_SENDER }}
    EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
  run: python scripts/run_report.py
```

---

## Technical Details

### Implementation

- **Location:** `src/ocean_report/config/loader.py`
- **Key Function:** `resolve_config_path(path: str | Path | None = None) -> Path`

### Path Resolution Logic

```python
def resolve_config_path(path: str | Path | None = None) -> Path:
    """Resolve config path to absolute Path, defaulting to project config."""
    if path:
        return Path(path).expanduser().resolve()
    
    # Try OCEAN_REPORT_CONFIG env var
    if env_path := os.getenv("OCEAN_REPORT_CONFIG"):
        return Path(env_path).expanduser().resolve()
    
    # Try project-relative path
    if project_root := find_dotenv("pyproject.toml"):
        return Path(project_root).parent / "configs" / "config.yaml"
    
    # Fallback to user config directory
    return Path.home() / ".config" / "ocean-report" / "config.yaml"
```

### Path Expansion Features

- **`~` expansion:** `~/configs/config.yaml` → `/Users/you/configs/config.yaml`
- **Relative paths:** Converted to absolute paths
- **Symlink resolution:** Follows symlinks to actual file
- **Cross-platform:** Works on Windows, macOS, Linux

---

## Best Practices

### Development
✅ Use default path (`configs/config.yaml`)  
✅ Commit config template to version control  
✅ Use `.env` for secrets  

### Production
✅ Use environment variable (`OCEAN_REPORT_CONFIG`)  
✅ Store config outside application directory  
✅ Use secrets management (AWS Secrets Manager, Azure Key Vault, etc.)  

### Testing
✅ Create separate test configs (`configs/test.yaml`)  
✅ Override via environment variable in tests  
✅ Use temporary directories for test configs  

### Docker
✅ Mount config as volume or use ConfigMaps  
✅ Set `OCEAN_REPORT_CONFIG` explicitly  
✅ Validate config exists in health checks  

---

## Migration Notes

**The old `constants.py` file was removed** because:
- Only used for config path resolution
- Path resolution now self-contained in `config/loader.py`
- Environment variable support more flexible than hardcoded path

**No migration needed** if you were running from repo root - everything works the same!

---

## See Also

- [Configuration Schema](../architecture/config.md) - Understanding config structure
- [Application Context Factory](./application-context-factory.md) - Using config with context
- [Logger Configuration](./logging.md) - Logging setup via config
