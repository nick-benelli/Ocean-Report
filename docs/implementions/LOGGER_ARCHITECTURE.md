# Logger Configuration Architecture

## 🏗️ What a Skilled Software Engineer Would Do (And What We Built)

### The Answer: **Hybrid Approach** (Config + Environment Variables)

We implemented a **three-layer configuration system** that follows industry best practices:

```
1. Code Defaults (Lowest Priority)
   ↓ overridden by
2. Config File (config.yaml)
   ↓ overridden by  
3. Environment Variables (Highest Priority)
```

---

## 🎯 Why This Approach?

### ✅ Best Practices We Follow:

1. **Configuration as Code**
   - Logging settings are documented in `config.yaml`
   - Version controlled and team-visible
   - Easy to review and understand

2. **Environment-Specific Flexibility**
   - Override via `.env` for different environments
   - No code changes needed between dev/staging/prod
   - Secrets stay out of version control

3. **Sensible Defaults**
   - Works out-of-the-box with no configuration
   - Backward compatible with existing code
   - Progressive enhancement

4. **12-Factor App Compliance**
   - Config in environment (when needed)
   - Strict separation of config and code
   - Easy to deploy across environments

---

## 📁 Configuration Hierarchy

### Layer 1: Code Defaults (Fallback)

```python
# src/ocean_report/logger.py
# Defaults if nothing is configured
configure_logger(output=LogOutput.CONSOLE, level=logging.INFO)
```

### Layer 2: Config File (Primary)

```yaml
# configs/config.yaml
logging:
  output: console          # or: file, both
  file_path: logs/ocean_report.log
  level: INFO             # or: DEBUG, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

**Use config.yaml when:**
- You want to document your logging strategy
- Settings are the same across environments
- You want version-controlled configuration

### Layer 3: Environment Variables (Override)

```bash
# .env
LOG_OUTPUT=both
LOG_FILE_PATH=logs/production.log
LOG_LEVEL=WARNING
```

**Use environment variables when:**
- Different settings per environment (dev vs prod)
- Local developer preferences
- CI/CD pipeline needs custom logging
- Temporary debugging sessions

---

## 🔄 How It Works

### Variable Resolution with Defaults

The config uses **environment variable substitution with fallback defaults**:

```yaml
# config.yaml
logging:
  output: ${LOG_OUTPUT:console}  # If LOG_OUTPUT not set, use "console"
  file_path: ${LOG_FILE_PATH:logs/ocean_report.log}
  level: ${LOG_LEVEL:INFO}
```

This means:
1. **First**, check if `LOG_OUTPUT` env var is set
2. **If not**, use the default value after the colon (`:console`)
3. **Result**: Always works, even with no `.env` file

---

## 💡 Usage Examples

### Example 1: Use Defaults (No Changes Needed)

```bash
# No configuration needed!
uv run scripts/run_report_no_email.py
```

**Result:** Console-only logging at INFO level ✅

---

### Example 2: Configure in config.yaml

```yaml
# configs/config.yaml
logging:
  output: both  # Console + file
  file_path: logs/production.log
  level: INFO
```

```bash
uv run scripts/run_report_no_email.py
```

**Result:** Logs to both console and `logs/production.log` ✅

---

### Example 3: Override with Environment Variables

```bash
# .env
LOG_OUTPUT=file
LOG_FILE_PATH=logs/debug.log
LOG_LEVEL=DEBUG
```

```bash
uv run scripts/run_report_no_email.py
```

**Result:** File-only logging at DEBUG level ✅

---

### Example 4: Quick Debug Session (Temporary Override)

```bash
# One-time override without changing files
LOG_OUTPUT=both LOG_LEVEL=DEBUG uv run scripts/run_report_no_email.py
```

**Result:** Extra verbose debugging without permanent changes ✅

---

## 🎨 Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                  User Request                       │
│           "Run the ocean report"                    │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│              run_report()                           │
│  1. Load config from config.yaml                    │
│  2. Resolve env vars (e.g., ${LOG_OUTPUT:console})  │
│  3. Configure logger from resolved config           │
│  4. Execute workflow with configured logger         │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│         configure_logger()                          │
│  • Parse config settings                            │
│  • Map to LogOutput enum                            │
│  • Create handlers (console/file/both)              │
│  • Set log level and format                         │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│               Logger Ready                          │
│  • All modules use same logger instance             │
│  • Logs go to configured destinations               │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Deployment Scenarios

### Development Environment

```yaml
# config.yaml
logging:
  output: ${LOG_OUTPUT:both}
  file_path: ${LOG_FILE_PATH:logs/dev.log}
  level: ${LOG_LEVEL:DEBUG}
```

```bash
# .env (local developer machine)
LOG_OUTPUT=both
LOG_LEVEL=DEBUG
```

**Result:** See everything in terminal + file for debugging

---

### Production Environment

```yaml
# config.yaml (same file!)
logging:
  output: ${LOG_OUTPUT:both}
  file_path: ${LOG_FILE_PATH:logs/ocean_report.log}
  level: ${LOG_LEVEL:INFO}
```

```bash
# .env (production server)
LOG_OUTPUT=file
LOG_FILE_PATH=/var/log/ocean-report/production.log
LOG_LEVEL=WARNING
```

**Result:** File-only logging, warnings and errors only

---

### CI/CD Pipeline

```bash
# GitHub Actions / Jenkins / etc.
export LOG_OUTPUT=both
export LOG_FILE_PATH=artifacts/test-run.log
export LOG_LEVEL=INFO

uv run scripts/run_report_no_email.py
```

**Result:** Pipeline can download log artifacts after run

---

## 🔐 Security & Best Practices

### ✅ DO:
- ✅ Keep logging config in `config.yaml` for documentation
- ✅ Use environment variables for secrets (API keys, passwords)
- ✅ Use environment variables for environment-specific settings
- ✅ Set appropriate log levels for each environment
- ✅ Rotate log files in production
- ✅ Use `.gitignore` to exclude `.env` and log files

### ❌ DON'T:
- ❌ Hard-code log file paths in source code
- ❌ Commit `.env` files to git
- ❌ Use DEBUG level in production
- ❌ Log sensitive information (passwords, tokens)
- ❌ Let log files grow unbounded

---

## 📊 Comparison: Config vs Env Vars

| Aspect | Config File | Environment Variables |
|--------|-------------|----------------------|
| **Documentation** | ✅ Self-documenting | ❌ Hidden unless listed |
| **Version Control** | ✅ Tracked in git | ❌ Not tracked |
| **Team Visibility** | ✅ Everyone sees it | ⚠️ May vary per dev |
| **Per-Environment** | ❌ Same for all | ✅ Different per env |
| **Secrets** | ❌ Unsafe | ✅ Safe |
| **Override Priority** | Medium | High |
| **Default Values** | ✅ Easy | ⚠️ Requires fallback |

---

## 🧪 Testing Different Configurations

### Test 1: Default (Console Only)
```bash
uv run scripts/run_report_no_email.py
```

### Test 2: Config-Based (Both Console + File)
```bash
uv run scripts/test_config_logging.py
```

### Test 3: Env Override (File Only)
```bash
LOG_OUTPUT=file LOG_FILE_PATH=logs/test.log uv run scripts/run_report_no_email.py
```

### Test 4: Debug Level
```bash
LOG_LEVEL=DEBUG uv run scripts/run_report_no_email.py
```

---

## 📖 Related Documentation

- [LOGGER_GUIDE.md](LOGGER_GUIDE.md) - How to use the logger API
- [CONFIG_PATH_RESOLUTION.md](CONFIG_PATH_RESOLUTION.md) - Config loading details
- [.env.template](../.env.template) - Environment variable examples

---

## 🎓 Summary: Why This Architecture?

1. **Defaults in code** = Works immediately, no setup needed
2. **Config in YAML** = Documented, version-controlled, team-shared
3. **Override with env** = Flexible per environment, secure for secrets

This follows the **Principle of Least Surprise**:
- Developers see config in `config.yaml`
- DevOps can override with environment variables
- No configuration works out-of-the-box
- Everything is explicit and discoverable

**This is what skilled software engineers do.** ✨
