# ApplicationContext Factory Design Document

## Overview

The `create_application_context()` factory provides a single, unambiguous entry point for constructing `ApplicationContext` instances. It prioritizes simplicity, maintainability, and explicit behavior over maximum flexibility.

## Design Decisions

### 1. Keyword-Only Parameters

```python
def create_application_context(
    *,  # Forces keyword-only arguments
    context: ApplicationContext | None = None,
    config: AppConfig | None = None,
    config_path: str | Path | None = None,
) -> ApplicationContext:
```

**Rationale:**
- Prevents accidental positional argument passing
- Makes call sites self-documenting: `create_application_context(config=my_config)`
- Reduces risk of parameter order mistakes
- Common Python best practice for functions with multiple optional parameters

### 2. Mutual Exclusivity Validation

The factory enforces that only one source of configuration can be provided:

```python
provided_params = sum([
    context is not None,
    config is not None,
    config_path is not None,
])

if provided_params > 1:
    raise ValueError(...)
```

**Rationale:**
- Eliminates ambiguity about which configuration source takes precedence
- Fail-fast behavior prevents subtle bugs from conflicting inputs
- Makes the API contract explicit and easy to reason about
- Validation happens before any I/O operations (efficient early failure)

**Alternative Considered:** Precedence rules (e.g., "context wins if provided")
- **Rejected:** Implicit precedence rules are harder to remember and lead to confusion
- **Rejected:** May hide bugs where multiple parameters are passed accidentally

### 3. No `client` Parameter

The factory does NOT accept a pre-built `ApiClient`:

```python
# NOT SUPPORTED:
create_application_context(config=config, client=my_client)  # ❌
```

**Rationale:**
- Prevents inconsistency between `config` and `client` state
- Configuration remains the single source of truth
- Eliminates a category of bugs where client and config don't match
- Simplifies testing (mock the config, not the client)
- Aligns with "composition from configuration" principle

**Use Case Analysis:**
- **Testing:** Use `config` parameter with test configuration
- **Custom client:** Modify `AppConfig.api` settings instead
- **Shared session:** Future enhancement to ApiClient factory if needed

### 4. Context Pass-Through (Rule 1)

```python
if context is not None:
    return context
```

**Rationale:**
- Enables clean dependency injection patterns
- Zero overhead when context already exists
- Useful for optional parameters in functions:
  ```python
  def process(context: ApplicationContext | None = None):
      ctx = create_application_context(context=context)
      # Always has a valid context here
  ```
- Makes factory composable and transparent

### 5. Cached vs. Uncached Config Loading

- **Rule 4 (no parameters):** Uses `get_settings()` → **cached**
- **Rule 3 (config_path):** Uses `load_app_config(path)` → **uncached**

```python
# Default: cached for performance
config = get_settings()

# Explicit path: uncached for flexibility
config = load_app_config(config_path)
```

**Rationale:**
- Default path (production) benefits from caching for repeated calls
- Explicit path suggests intent to load specific configuration
- Matches existing config loader API semantics
- Allows explicit control when needed without changing default behavior

### 6. Path Flexibility

Accepts both `str` and `Path` for `config_path`:

```python
config_path: str | Path | None = None
```

**Rationale:**
- Modern Python code often uses `pathlib.Path`
- String paths remain convenient for quick scripts
- Underlying `load_app_config()` already handles both
- No conversion needed (just pass through)

### 7. Four Explicit Rules

The factory implements exactly four rules:

1. **Context pass-through** → No-op, return as-is
2. **From config** → Create client, build context
3. **From path** → Load config, create client, build context
4. **Default** → Load cached config, create client, build context

**Rationale:**
- Small, finite set of use cases is easy to understand and test
- Each rule maps to a clear user intent
- Linear control flow (no nested conditionals)
- Easy to document and explain
- Covers all practical production and testing scenarios

**Alternative Considered:** Builder pattern with method chaining
- **Rejected:** Overkill for this simple use case
- **Rejected:** Adds complexity without providing value
- **Rejected:** Less discoverable than a single function

### 8. Frozen ApplicationContext

The factory returns a frozen (immutable) `ApplicationContext`:

```python
@dataclass(frozen=True, slots=True)
class ApplicationContext:
    config: AppConfig
    client: ApiClient
```

**Rationale:**
- Prevents accidental mutation after creation
- Makes context safe to pass across threads
- Encourages creating new contexts rather than modifying existing ones
- Aligns with functional programming principles
- `slots=True` adds memory efficiency

### 9. Comprehensive Error Messages

```python
raise ValueError(
    "Only one of 'context', 'config', or 'config_path' may be provided. "
    "Multiple parameters create ambiguous configuration sources."
)
```

**Rationale:**
- Clear explanation of what went wrong
- Suggests the fix (use only one parameter)
- Explains *why* this is an error (ambiguity)
- Improves developer experience

### 10. Type Annotations Throughout

```python
from __future__ import annotations  # Enables postponed evaluation

def create_application_context(
    *,
    context: ApplicationContext | None = None,
    config: AppConfig | None = None,
    config_path: str | Path | None = None,
) -> ApplicationContext:
```

**Rationale:**
- Enables static type checking with mypy/pyright
- Self-documenting code
- IDE autocomplete and hints
- Catches bugs at development time
- Modern Python best practice (PEP 484, 585, 604)

## Anti-Patterns Prevented

### ❌ Implicit Defaults
```python
# BAD: Which config file is loaded?
context = old_factory()
```

### ✅ Explicit Behavior
```python
# GOOD: Clear intent
context = create_application_context()  # Uses get_settings()
```

### ❌ Precedence Rules
```python
# BAD: What happens here?
context = create_application_context(
    config=config1,
    config_path="other.yaml"
)
```

### ✅ Mutual Exclusivity
```python
# GOOD: Raises ValueError with clear message
```

### ❌ Configuration Drift
```python
# BAD: Client and config may be inconsistent
context = create_application_context(
    config=config,
    client=manually_created_client  # Doesn't match config
)
```

### ✅ Single Source of Truth
```python
# GOOD: Client always created from config
context = create_application_context(config=config)
```

## Testing Strategy

### Unit Tests
- Test each rule in isolation
- Validate mutual exclusivity
- Verify no side effects
- Mock dependencies (`get_settings`, `load_app_config`, `create_api_client`)

### Integration Tests
- Test with real config files
- Verify end-to-end context creation
- Test default configuration path

### Edge Cases
- `None` explicitly passed vs. parameter omitted
- String vs. Path for config_path
- Empty config files
- Invalid YAML

## Performance Considerations

### Caching
- Default path uses `get_settings()` with `@lru_cache`
- Subsequent calls are O(1) hash lookups
- No repeated file I/O or YAML parsing

### Validation Overhead
- Parameter counting is O(1)
- Validation happens before I/O (fail-fast)
- Negligible performance impact

### Object Creation
- Single `ApiClient` instance per context
- No unnecessary object duplication
- Frozen dataclass has minimal overhead

## Migration Path

If you need to migrate from an older factory pattern:

```python
# Old pattern
context = ApplicationContext(
    config=load_config(),
    client=create_api_client(load_config())
)

# New pattern
context = create_application_context()
```

The new factory eliminates redundant config loading and ensures consistency.

## Future Enhancements

Possible extensions without breaking changes:

### 1. Session Pooling
```python
# Future: Add session parameter to create_api_client
def create_application_context(
    *,
    session: requests.Session | None = None,
    ...
) -> ApplicationContext:
    client = create_api_client(config, session=session)
```

### 2. Context Protocols
```python
# Future: Support different context types
def create_application_context(
    *,
    context_type: type[ApplicationContext] = ApplicationContext,
    ...
) -> ApplicationContext:
```

### 3. Validation Hooks
```python
# Future: Add validation callbacks
def create_application_context(
    *,
    validators: list[Callable[[AppConfig], None]] | None = None,
    ...
) -> ApplicationContext:
```

## Conclusion

This factory design prioritizes:
1. **Simplicity** – Four clear rules, linear control flow
2. **Explicitness** – No magic, no hidden behavior
3. **Safety** – Immutable results, validated inputs
4. **Maintainability** – Easy to understand, test, and extend
5. **Performance** – Efficient caching, minimal overhead

The design makes the common case (default configuration) trivial while supporting less common cases (custom configs, testing) without introducing complexity or ambiguity.
