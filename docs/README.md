# Ocean Report Documentation

Welcome to the Ocean Report documentation! This guide will help you understand, configure, and extend the Ocean Report application.

---

## 📚 What is Ocean Report?

Ocean Report is a Python application that generates and emails daily coastal conditions reports. It fetches data from multiple weather APIs (NOAA, NDBC, Open-Meteo) and compiles water temperature, tide predictions, and wind forecasts into a formatted email sent to subscribers.

**Key Features:**
- 🌡️ Real-time water temperature from NOAA
- 🌊 Tide predictions (high/low tides filtered for daytime)
- 🌬️ Wind forecasts with direction classification (offshore/onshore/cross-shore)
- 📧 Automated email delivery via SMTP
- 🔄 Configurable retry logic with SSL error handling
- 📝 Comprehensive logging (console, file, or both)
- 🧪 Email preview mode for testing

---

## 🚀 Quick Start

### For First-Time Users

1. **Understand the System**
   - Read [Architecture Overview](architecture/README.md) to understand how components fit together
   - Review [Workflows](architecture/workflows.md) to see the complete data flow

2. **Set Up Configuration**
   - Follow [Configuration Setup Guide](guides/config-setup.md)
   - Configure logging with [Logging Guide](guides/logging.md)

3. **Test Without Sending**
   ```bash
   uv run scripts/run_report_no_email.py
   ```
   - See [Email Preview Guide](guides/email-preview.md)

4. **Send Your First Report**
   ```bash
   uv run scripts/run_report.py
   ```

---

## 📖 Documentation Structure

### 🏗️ Architecture Documentation (`architecture/`)

Comprehensive technical documentation explaining how each component works:

| Component | Description |
|-----------|-------------|
| [**README.md**](architecture/README.md) | 📌 **START HERE** - System overview, architecture diagrams, component relationships |
| [api_client.md](architecture/api_client.md) | HTTP transport layer with retry logic and SSL handling |
| [application.md](architecture/application.md) | Dependency injection container (ApplicationContext) |
| [config.md](architecture/config.md) | Configuration loading, validation, and path resolution |
| [emailer.md](architecture/emailer.md) | Email formatting and SMTP delivery |
| [endpoints.md](architecture/endpoints.md) | API-specific endpoint implementations (NOAA, NDBC, Open-Meteo) |
| [models.md](architecture/models.md) | Pydantic data models for type-safe schemas |
| [services.md](architecture/services.md) | Service layer - thin wrappers around endpoints |
| [use_cases.md](architecture/use_cases.md) | Business logic orchestration layer |
| [utils.md](architecture/utils.md) | Pure utility functions (date, wind calculations) |
| [workflows.md](architecture/workflows.md) | Top-level orchestration that coordinates everything |
| [logger.md](architecture/logger.md) | Logging configuration and usage |

**When to use:** Understanding the codebase, debugging, extending functionality, architecture decisions

---

### 📘 Practical Guides (`guides/`)

Step-by-step guides for common tasks:

| Guide | Description |
|-------|-------------|
| [**config-setup.md**](guides/config-setup.md) | Configuration path resolution, environment variables, Docker/K8s deployment |
| [**logging.md**](guides/logging.md) | Logging configuration (console/file/both), log levels, formatting |
| [**email-preview.md**](guides/email-preview.md) | Preview emails before sending, HTML/text output, terminal commands |
| [**api-client-factory.md**](guides/api-client-factory.md) | Creating API clients from configuration, testing patterns |
| [**application-context-factory.md**](guides/application-context-factory.md) | Creating application contexts, dependency injection patterns |

**When to use:** Setting up the application, configuring for different environments, testing, troubleshooting

---

## 🎯 Common Tasks

### Setting Up for Development

1. **Clone and install dependencies:**
   ```bash
   git clone https://github.com/nick-benelli/Ocean-Report.git
   cd Ocean-Report
   uv sync
   ```

2. **Configure environment:**
   ```bash
   cp .env.template .env
   # Edit .env with your settings
   ```

3. **Test configuration:**
   ```bash
   uv run scripts/run_report_no_email.py
   ```

**See:** [Configuration Setup Guide](guides/config-setup.md)

---

### Running in Different Environments

#### Local Development (Default)
```bash
uv run scripts/run_report_no_email.py  # Preview mode
```

#### Production
```bash
uv run scripts/run_report.py  # Sends email
```

#### Custom Config
```bash
OCEAN_REPORT_CONFIG=configs/custom.yaml uv run scripts/run_report.py
```

#### Docker
```bash
docker run -e OCEAN_REPORT_CONFIG=/app/config.yaml ocean-report
```

**See:** [Configuration Setup Guide](guides/config-setup.md)

---

### Configuring Logging

#### Console Only (Default)
```yaml
# config.yaml
logging:
  output: console
  level: INFO
```

#### File Only (Production)
```yaml
logging:
  output: file
  file_path: logs/production.log
  level: INFO
```

#### Both (Development)
```yaml
logging:
  output: both
  file_path: logs/debug.log
  level: DEBUG
```

**See:** [Logging Guide](guides/logging.md)

---

### Testing Changes

1. **Preview email without sending:**
   ```bash
   uv run scripts/run_report_no_email.py
   ```

2. **Check HTML preview:**
   ```bash
   open logs/email-previews/email_preview_*.html
   ```

3. **Compare with previous:**
   ```bash
   diff $(ls -t logs/email-previews/*.txt | sed -n '2p') \
        $(ls -t logs/email-previews/*.txt | sed -n '1p')
   ```

**See:** [Email Preview Guide](guides/email-preview.md)

---

## 🔍 Finding What You Need

### By Role

#### **New Developer / Fresh Eyes**
1. Start with [Architecture Overview](architecture/README.md)
2. Understand [Workflows](architecture/workflows.md) (the orchestrator)
3. Follow the data flow through [Use Cases](architecture/use_cases.md) → [Services](architecture/services.md) → [Endpoints](architecture/endpoints.md)

#### **DevOps / Deployment**
1. [Configuration Setup](guides/config-setup.md) - Path resolution, env vars
2. [Logging Configuration](guides/logging.md) - Production logging setup
3. [Application Context Factory](guides/application-context-factory.md) - Environment-specific configs

#### **QA / Testing**
1. [Email Preview Guide](guides/email-preview.md) - Test without sending
2. [Logging Guide](guides/logging.md) - Debug output
3. [Application Context Factory](guides/application-context-factory.md) - Test contexts

#### **Maintainer / Debugger**
1. [Architecture Docs](architecture/) - Component internals
2. [Logger Architecture](architecture/logger.md) - Logging system
3. [API Client](architecture/api_client.md) - Retry logic and error handling

---

### By Task

#### **Understanding the System**
- [Architecture README](architecture/README.md) - System overview
- [Workflows](architecture/workflows.md) - Complete execution flow
- [Use Cases](architecture/use_cases.md) - Business logic

#### **Configuration**
- [Config Setup Guide](guides/config-setup.md) - Path resolution
- [Configuration Component](architecture/config.md) - How config loading works
- [Application Context](architecture/application.md) - DI container

#### **API Integration**
- [Endpoints](architecture/endpoints.md) - API implementations
- [Services](architecture/services.md) - Service layer
- [Models](architecture/models.md) - Data schemas

#### **Email System**
- [Emailer Component](architecture/emailer.md) - Formatting and sending
- [Email Preview Guide](guides/email-preview.md) - Testing emails

#### **Testing**
- [API Client Factory Guide](guides/api-client-factory.md) - Mock clients
- [Application Context Factory Guide](guides/application-context-factory.md) - Test contexts
- [Email Preview Guide](guides/email-preview.md) - Preview without sending

---

## 📐 Architecture at a Glance

```
Entry Points (scripts)
         ↓
┌────────────────────────────────────┐
│   Workflows Layer                  │  ← Top-level orchestration
│   (workflows/report_runner.py)    │
└────────────────┬───────────────────┘
                 ↓
┌────────────────────────────────────┐
│   Use Cases Layer                  │  ← Business logic
│   (water_temp, tides, wind)       │
└────────────────┬───────────────────┘
                 ↓
┌────────────────────────────────────┐
│   Services Layer                   │  ← Data fetching
│   (fetch_water_temp, etc.)        │
└────────────────┬───────────────────┘
                 ↓
┌────────────────────────────────────┐
│   Endpoints Layer                  │  ← API-specific logic
│   (NOAA, NDBC, Open-Meteo)       │
└────────────────┬───────────────────┘
                 ↓
┌────────────────────────────────────┐
│   API Client Layer                 │  ← HTTP transport
│   (retry, SSL, timeout handling)  │
└────────────────────────────────────┘
```

**Cross-cutting concerns:**
- **Config** - Loaded once, passed via ApplicationContext
- **Logger** - Configured at startup, used everywhere
- **Models** - Type-safe data schemas with Pydantic

**See:** [Architecture Overview](architecture/README.md) for detailed diagrams

---

## 🧪 Testing Strategy

### Unit Tests
- Mock API responses
- Test business logic in isolation
- Use custom test contexts

**Example:**
```python
@pytest.fixture
def test_context():
    config = AppConfig(api=ApiConfig(timeout_seconds=5, verify_ssl=False))
    return create_application_context(config=config)
```

**See:** [Application Context Factory](guides/application-context-factory.md)

---

### Integration Tests
- Test with real APIs (preview mode)
- Verify complete workflows
- Check email formatting

**Example:**
```bash
uv run scripts/run_report_no_email.py
# Check logs/email-previews/
```

**See:** [Email Preview Guide](guides/email-preview.md)

---

## 🔧 Troubleshooting

### Common Issues

| Issue | Solution | Guide |
|-------|----------|-------|
| Config file not found | Set `OCEAN_REPORT_CONFIG` env var | [Config Setup](guides/config-setup.md#troubleshooting) |
| No logs appearing | Check log level and output config | [Logging](guides/logging.md#troubleshooting) |
| Email preview not created | Verify running in preview mode | [Email Preview](guides/email-preview.md#troubleshooting) |
| API timeout errors | Check network, increase timeout | [API Client](architecture/api_client.md#common-issues) |
| SSL verification errors | Check retry settings in config | [API Client](architecture/api_client.md#ssl-error-recovery) |

---

## 📞 Support

### Getting Help

1. **Check documentation:**
   - Search architecture docs for component details
   - Check guides for practical how-tos
   - Review troubleshooting sections

2. **Enable debug logging:**
   ```yaml
   logging:
     output: both
     level: DEBUG
   ```

3. **Review logs:**
   ```bash
   tail -f logs/ocean_report.log
   ```

4. **Preview mode:**
   - Test without sending emails
   - Review HTML and text previews
   - Compare with previous runs

---

## 🚀 Next Steps

### For Developers
1. Read [Architecture Overview](architecture/README.md)
2. Explore component documentation in `architecture/`
3. Run tests: `pytest tests/`
4. Try modifying a use case or endpoint

### For DevOps
1. Review [Configuration Setup](guides/config-setup.md)
2. Set up [Logging](guides/logging.md) for your environment
3. Test deployment with [Email Preview](guides/email-preview.md)
4. Configure scheduled execution (GitHub Actions, cron, etc.)

### For QA
1. Learn [Email Preview](guides/email-preview.md) workflow
2. Test different configurations
3. Review logs for errors
4. Verify email formatting and content

---

## 📝 Contributing

When contributing to Ocean Report:

1. **Understand the architecture** - Read relevant component docs
2. **Follow patterns** - Use existing factories, follow layer separation
3. **Update documentation** - Keep architecture docs and guides in sync
4. **Test thoroughly** - Unit tests + integration tests + email previews
5. **Log appropriately** - Use correct log levels, structured logging

**See:** Component documentation in `architecture/` for design patterns and principles

---

## 📂 Documentation Files

### Architecture Documentation (Technical Deep Dives)
- [architecture/README.md](architecture/README.md) - System overview
- [architecture/api_client.md](architecture/api_client.md)
- [architecture/application.md](architecture/application.md)
- [architecture/config.md](architecture/config.md)
- [architecture/emailer.md](architecture/emailer.md)
- [architecture/endpoints.md](architecture/endpoints.md)
- [architecture/logger.md](architecture/logger.md)
- [architecture/models.md](architecture/models.md)
- [architecture/services.md](architecture/services.md)
- [architecture/use_cases.md](architecture/use_cases.md)
- [architecture/utils.md](architecture/utils.md)
- [architecture/workflows.md](architecture/workflows.md)

### Practical Guides (How-To)
- [guides/api-client-factory.md](guides/api-client-factory.md)
- [guides/application-context-factory.md](guides/application-context-factory.md)
- [guides/config-setup.md](guides/config-setup.md)
- [guides/email-preview.md](guides/email-preview.md)
- [guides/logging.md](guides/logging.md)

---

**Last Updated:** June 17, 2026  
**Ocean Report Version:** 2.0 (remodel branch)
