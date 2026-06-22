# ApiClient Factory - Design Decisions

## Overview

This document explains the architectural decisions behind the `create_api_client` factory function and the reasoning for its design.

---

## Core Design Principles

### 1. **Pure Factory Function (No Side Effects)**

**Decision:** The factory is implemented as a pure function that doesn't load configuration from disk or maintain global state.

**Rationale:**
- **Testability:** Pure functions are easier to test - no mocking of file I/O required
- **Predictability:** Same input always produces equivalent output
- **Composability:** Can be used in any context without hidden dependencies
- **Thread-safety:** No shared mutable state means no concurrency issues

**Alternative Rejected:** Singleton pattern where factory loads config internally
```python
# ❌ Rejected approach
def create_api_client() -> ApiClient:
    config = load_config("config.yaml")  # Hidden file I/O
    return ApiClient(...)
```

**Why Rejected:** 
- Hard to test (requires filesystem mocking)
- Inflexible (can't use programmatically created configs)
- Violates separation of concerns (factory shouldn't handle I/O)

---

### 2. **Dependency Injection Over Service Locator**

**Decision:** Configuration is passed explicitly as a parameter rather than retrieved from a global registry.

**Rationale:**
- **Explicit dependencies:** Clear what the factory needs to work
- **Multiple configurations:** Easy to create clients with different configs
- **No hidden coupling:** No dependency on global state
- **Better for testing:** Can pass test configs without touching global state

**Alternative Rejected:** Global configuration registry
```python
# ❌ Rejected approach
def create_api_client() -> ApiClient:
    config = ConfigRegistry.get_global_config()
    return ApiClient(...)
```

**Why Rejected:**
- Hard to test (requires registry setup/teardown)
- Single configuration limits flexibility
- Hidden dependency on global state
- Difficult to run multiple configs in same process

---

### 3. **Optional Session Injection**

**Decision:** Allow passing a custom `requests.Session` but create one by default.

**Rationale:**
- **Default simplicity:** Most callers don't need custom sessions
- **Testing flexibility:** Can inject mock sessions for unit tests
- **Session pooling:** Advanced users can share sessions across clients
- **Custom configuration:** Allows pre-configured sessions with headers, auth, etc.

**Implementation:**
```python
def create_api_client(
    config: AppConfig,
    session: requests.Session | None = None,  # Optional
) -> ApiClient:
    return ApiClient(..., session=session)
```

**Use Cases:**
- **Default (None):** Standard usage, ApiClient creates its own session
- **Mock session:** Unit testing without HTTP calls
- **Shared session:** Connection pooling across multiple clients
- **Custom session:** Pre-configured with auth tokens, headers, etc.

---

### 4. **Configuration Mapping (Not Passthrough)**

**Decision:** Explicitly map each config field to ApiClient parameters rather than unpacking.

**Rationale:**
- **Clarity:** Easy to see exactly what's being configured
- **Type safety:** IDE and type checkers can verify all mappings
- **Maintainability:** Changes to config schema are obvious
- **Documentation:** Self-documenting - shows all supported parameters

**Current Implementation:**
```python
return ApiClient(
    timeout=config.api.timeout_seconds,
    verify_ssl=config.api.verify_ssl,
    retry_insecure_on_ssl_error=config.api.retry_insecure_on_ssl_error,
    max_retries=config.api.max_retries,
    backoff_seconds=config.api.backoff_seconds,
    session=session,
)
```

**Alternative Rejected:** Dictionary unpacking
```python
# ❌ Rejected approach
return ApiClient(**config.api.model_dump(), session=session)
```

**Why Rejected:**
- Fragile - breaks if config field names differ from constructor params
- Type-unsafe - no compile-time checking
- Hard to debug - unclear what values are being passed
- Poor discoverability - harder for IDE autocomplete

---

### 5. **Single Responsibility Principle**

**Decision:** Factory only creates clients; it doesn't configure them post-creation.

**Rationale:**
- **Clear boundary:** Construction is separate from configuration
- **Client immutability:** All settings defined at creation time
- **Predictable behavior:** Client state doesn't change after creation
- **Simpler testing:** Test creation separately from usage

**What Factory Does:**
- ✅ Extract configuration values
- ✅ Construct ApiClient instance
- ✅ Pass session if provided

**What Factory Doesn't Do:**
- ❌ Load configuration files
- ❌ Validate configuration (done by Pydantic schemas)
- ❌ Register clients globally
- ❌ Configure client after creation
- ❌ Manage client lifecycle

---

### 6. **Type Hints and Documentation**

**Decision:** Comprehensive type hints and detailed docstrings.

**Rationale:**
- **IDE support:** Better autocomplete and inline documentation
- **Type checking:** Catch errors before runtime with mypy/pyright
- **Self-documentation:** Code explains itself
- **API contracts:** Clear expectations for callers

**Implementation:**
```python
def create_api_client(
    config: AppConfig,  # Type hint
    session: requests.Session | None = None,  # Optional with default
) -> ApiClient:  # Return type
    """Detailed docstring with Args, Returns, Example..."""
```

**Benefits:**
- Mypy can verify all config access is valid
- IDEs show parameter types and documentation
- Refactoring is safer (type changes propagate)
- Examples in docstring serve as living documentation

---

## Architectural Patterns

### Factory Pattern Benefits

The factory pattern provides:

1. **Encapsulation:** Construction logic hidden from callers
2. **Flexibility:** Easy to change how clients are created
3. **Consistency:** All clients created the same way
4. **Testability:** Easy to mock or stub the factory

### Separation of Concerns

```
┌─────────────────┐
│  config.yaml    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ConfigLoader    │  ← Handles I/O and parsing
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ AppConfig       │  ← Validates and stores config
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Factory         │  ← Creates client from config
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ApiClient       │  ← Makes HTTP requests
└─────────────────┘
```

Each layer has a single responsibility and can be tested independently.

---

## Trade-offs and Considerations

### Verbosity vs. Flexibility

**Trade-off:** Explicit field mapping is more verbose than unpacking.

**Decision:** Choose explicitness for better maintainability.

**Impact:**
- ➕ Changes are obvious and safe
- ➕ Type checking catches errors
- ➖ More lines of code
- ➖ Updates needed when fields change

**Mitigation:** This is a small factory with only 5 config fields - verbosity is minimal.

---

### Session Injection Complexity

**Trade-off:** Optional session parameter adds complexity for a rarely-used feature.

**Decision:** Include it for testability and advanced use cases.

**Impact:**
- ➕ Unit testing without HTTP calls
- ➕ Session sharing for performance
- ➕ Custom session configuration
- ➖ Slightly more complex signature
- ➖ Need to handle None case

**Mitigation:** Default to None makes common case simple; docs explain advanced usage.

---

### No Validation in Factory

**Trade-off:** Factory assumes config is valid; doesn't re-validate.

**Decision:** Trust Pydantic validation at config load time.

**Impact:**
- ➕ No duplicate validation
- ➕ Faster client creation
- ➕ Single source of validation logic
- ➖ Invalid config could reach factory
- ➖ Less defensive programming

**Mitigation:** AppConfig schema ensures config is validated before reaching factory.

---

## Best Practices

### Do's ✅

1. **Always load config first**
   ```python
   config = load_config("config.yaml")  # Validates
   client = create_api_client(config)   # Uses validated config
   ```

2. **Use factory consistently**
   ```python
   # Don't create ApiClient directly in application code
   client = create_api_client(config)  # ✅ Good
   ```

3. **Inject sessions for testing**
   ```python
   mock_session = Mock(spec=requests.Session)
   client = create_api_client(config, session=mock_session)
   ```

4. **Create multiple clients when needed**
   ```python
   noaa_client = create_api_client(config)
   ndbc_client = create_api_client(config)
   # Independent clients, no shared state
   ```

### Don'ts ❌

1. **Don't bypass the factory**
   ```python
   # ❌ Don't do this in application code
   client = ApiClient(timeout=10.0, verify_ssl=True, ...)
   ```
   **Why:** Loses configuration management benefits

2. **Don't modify config after loading**
   ```python
   # ❌ Don't mutate config
   config = load_config("config.yaml")
   config.api.timeout_seconds = 20.0  # Pydantic models are frozen
   ```
   **Why:** Config should be immutable; create new config instead

3. **Don't create global singletons**
   ```python
   # ❌ Don't do this
   GLOBAL_CLIENT = create_api_client(config)
   ```
   **Why:** Makes testing harder, couples code to global state

4. **Don't mix factory and direct construction**
   ```python
   # ❌ Inconsistent
   client1 = create_api_client(config)  # Via factory
   client2 = ApiClient(timeout=10.0, ...)  # Direct construction
   ```
   **Why:** Choose one pattern and stick with it

---

## Future Considerations

### Potential Enhancements

1. **Named client profiles**
   ```python
   # Future possibility
   client = create_api_client(config, profile="slow-endpoint")
   ```

2. **Client pooling**
   ```python
   # Future possibility
   pool = create_client_pool(config, size=10)
   ```

3. **Async client factory**
   ```python
   # Future possibility
   async_client = create_async_api_client(config)
   ```

4. **Telemetry/monitoring integration**
   ```python
   # Future possibility
   client = create_api_client(config, telemetry=metrics_client)
   ```

### Backward Compatibility

The current design supports future enhancements without breaking changes:
- New optional parameters can be added (default to None)
- Config schema can be extended (existing fields unchanged)
- Factory can delegate to specialized factories if needed

---

## Summary

The `create_api_client` factory is designed to be:

- **Simple:** One function, one purpose
- **Pure:** No side effects or hidden dependencies
- **Flexible:** Supports testing and advanced use cases
- **Type-safe:** Full type hints for tooling support
- **Maintainable:** Clear, explicit, and well-documented
- **Testable:** Easy to unit test without mocking I/O

This design provides a solid foundation that can evolve with the project's needs while maintaining clarity and simplicity.
