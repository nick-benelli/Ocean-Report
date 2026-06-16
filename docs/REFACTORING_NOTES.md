# Configuration Loader Refactoring

## Overview

The configuration loader was refactored for simplicity and clarity. The result is a focused, easy-to-understand module with clear responsibilities and no unnecessary complexity.

## What Changed

### Before
- 350+ lines of code
- Extensive docstrings
- Legacy aliases for backward compatibility
- Module-level side effects (`load_dotenv()` at import)
- Excessive documentation

### After  
- **80 lines total** ⚡
- Concise docstrings
- No aliases - one clear way to do each thing
- No import-time side effects
- Focused on clarity

## API (7 Functions)

```python
# Path handling
resolve_config_path()      # str|Path → Path

# Loading (uncached)
load_raw_config()          # → dict (with env substitution)
load_app_config()          # → AppConfig (validated)

# Cached access
get_settings()             # → AppConfig (cached)
get_config_dict()          # → dict (cached)

# Cache management
clear_config_cache()       # Clear cache
reload_config()            # Clear + reload
```

## Function Flow

```
resolve_config_path()
        ↓
load_raw_config()          # load_dotenv() called here
        ↓
load_app_config()
        ↓
get_settings()             # Cached via _cached_load()
```

## Key Improvements

### 1. Clean Separation
Each function has one clear job:
- `resolve_config_path()` - Path resolution
- `load_raw_config()` - YAML + env substitution  
- `load_app_config()` - Validation
- `get_settings()` - Cached access

### 2. Modern Path Handling
```python
# Before
def get_config_path(path: str | PathLike[str] | None = None) -> str:
    candidate = str(path or constants.CONFIG_PATH)
    return os.path.abspath(os.path.expanduser(candidate))

# After
def resolve_config_path(path: str | Path | None = None) -> Path:
    candidate = path if path is not None else constants.CONFIG_PATH
    return Path(candidate).expanduser().resolve()
```

### 3. Clear Naming
- `load_*` = uncached (always reads disk)
- `get_*` = cached (reuses previous loads)

### 4. No Import-Time Side Effects
```python
# Before: Side effect at import
load_dotenv()  # At module level

# After: Called when needed
def load_raw_config(...):
    load_dotenv()  # Inside function
    ...
```

### 5. Appropriate Function Name
`load_app_config()` instead of `load_config()` makes it clear it returns `AppConfig`, not a raw dict.

## Design Decisions

### Why `load_app_config` not `load_config`?
Makes the return type obvious:
- `load_raw_config()` → `dict`
- `load_app_config()` → `AppConfig`

### Why move `load_dotenv()` into `load_raw_config()`?
Importing a module should not mutate process state. This keeps imports side-effect free.

### Why no backward compatibility?
This is application code, not a library. Simplicity > compatibility for internal code.

### Why short docstrings?
The audience is future maintainers of this codebase, not external users. The code is self-documenting.

### Why unlimited cache?
Applications typically use 1-2 config files. The simplicity of unlimited caching outweighs any memory concern.

## Usage Examples

### Production Code
```python
from ocean_report.config import get_settings

config = get_settings()  # Cached, efficient
smtp = config.email.smtp_server
```

### Testing
```python
from ocean_report.config import load_app_config

config = load_app_config("test.yaml")  # Fresh, no cache
```

### Hot Reload
```python
from ocean_report.config import reload_config

config = reload_config()  # Clear cache + reload
```

## Benefits

1. **Easy to understand** - Can grasp the entire module in 30 seconds
2. **Easy to test** - Uncached loaders, no side effects
3. **Easy to maintain** - Minimal code, clear structure
4. **Type-safe** - pathlib.Path throughout
5. **Focused** - Does configuration loading, nothing else

## File Structure

```
src/ocean_report/config/
├── __init__.py          # 23 lines - public API
├── loader.py            # 80 lines - core logic
└── schemas.py           # (unchanged)
```

## Future Considerations

If needed later, consider:
- Logging for debugging
- Config file watching
- Environment-specific configs (dev/staging/prod)
- Remote config sources

But only add when actually needed. Keep it simple until you can't.

---

**Result:** A focused, maintainable configuration loader that does one thing well.
