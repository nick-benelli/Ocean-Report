# Practical Guides

This folder contains practical, hands-on guides for working with Ocean Report. These guides focus on **how to do specific tasks** rather than explaining internal architecture.

---

## 📘 Available Guides

### [Configuration Setup](./config-setup.md)
**What it covers:** Configuration path resolution, environment variables, and deployment strategies

**Use this when you need to:**
- Set up Ocean Report for the first time
- Deploy to Docker, Kubernetes, or cloud environments
- Use different configs for dev/staging/prod
- Debug "config file not found" errors
- Override config location with environment variables

**Key topics:**
- 4-level path resolution (env var → project → user dir → error)
- `OCEAN_REPORT_CONFIG` environment variable
- Docker and Kubernetes configuration
- Multi-environment config management
- Troubleshooting config issues

---

### [Logging Configuration](./logging.md)
**What it covers:** Logging setup, output destinations, log levels, and formatting

**Use this when you need to:**
- Configure where logs should go (console, file, or both)
- Set appropriate log levels for different environments
- Format log messages for production monitoring
- Debug issues with verbose logging
- Set up log rotation and cleanup

**Key topics:**
- Three output modes: console, file, or both
- Five log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Configuration via config.yaml and environment variables
- Custom log formats and timestamped log files
- Performance logging and structured logging patterns

---

### [Email Preview System](./email-preview.md)
**What it covers:** Testing emails without sending, HTML/text previews, and comparison workflows

**Use this when you need to:**
- Test email changes before sending to real recipients
- Review email formatting and content
- Compare email output across different runs
- Debug email formatting issues
- Archive email samples for reference

**Key topics:**
- Three outputs: console, HTML preview, text copy
- Opening and reviewing preview files
- Terminal commands for viewing and comparing previews
- Cleaning up old preview files
- Security and gitignore configuration

---

### [API Client Factory](./api-client-factory.md)
**What it covers:** Creating HTTP clients from configuration, testing with mocks, and factory design

**Use this when you need to:**
- Create API clients with proper configuration
- Write tests with mocked HTTP sessions
- Understand the factory pattern used in Ocean Report
- Create environment-specific clients (dev/prod)
- Override client settings for specific use cases

**Key topics:**
- Pure factory function with dependency injection
- Custom session injection for testing
- Configuration mapping and type safety
- Testing patterns with mock sessions
- Best practices and common pitfalls

---

### [Application Context Factory](./application-context-factory.md)
**What it covers:** Creating application contexts, dependency injection, and the four factory rules

**Use this when you need to:**
- Initialize the application with configuration
- Pass contexts through your application
- Write tests with custom test contexts
- Understand the four context creation rules
- Implement environment-specific initialization

**Key topics:**
- The four rules: pass-through, from config, from path, default
- Keyword-only parameters and mutual exclusivity
- Frozen immutable contexts
- Testing patterns and optional context parameters
- Decision tree and validation logic

---

## 🎯 Quick Reference

### By Task

| Task | Guide |
|------|-------|
| **First-time setup** | [Configuration Setup](./config-setup.md) |
| **Deploy to Docker/K8s** | [Configuration Setup](./config-setup.md) |
| **Debug with verbose logs** | [Logging Configuration](./logging.md) |
| **Test email changes** | [Email Preview System](./email-preview.md) |
| **Write unit tests** | [API Client Factory](./api-client-factory.md) + [Application Context Factory](./application-context-factory.md) |
| **Multi-environment config** | [Configuration Setup](./config-setup.md) + [Application Context Factory](./application-context-factory.md) |

---

### By User Role

#### 🚀 **DevOps / Deployment Engineer**
1. Start with [Configuration Setup](./config-setup.md)
2. Configure [Logging](./logging.md) for production
3. Use [Application Context Factory](./application-context-factory.md) for environment-specific configs

#### 🧪 **QA / Tester**
1. Learn [Email Preview System](./email-preview.md)
2. Use [Application Context Factory](./application-context-factory.md) for test contexts
3. Enable debug [Logging](./logging.md) when investigating issues

#### 👨‍💻 **Developer**
1. Review [Configuration Setup](./config-setup.md) for local development
2. Use [API Client Factory](./api-client-factory.md) and [Application Context Factory](./application-context-factory.md) for testing
3. Set up [Logging](./logging.md) for debugging

---

## 🔗 Related Documentation

### For Architecture & Design
See the [architecture](../architecture/) folder for detailed technical documentation on how components work internally.

### For Quick Start
See the [main docs README](../README.md) for a complete overview and quick start guide.

---

## 📝 Guide Format

Each guide follows a consistent structure:

- **Overview** - What the guide covers
- **Quick Start** - Get started immediately
- **Basic Usage** - Common patterns and examples
- **Advanced Usage** - Complex scenarios and customization
- **Troubleshooting** - Common issues and solutions
- **Best Practices** - Recommended approaches
- **See Also** - Related documentation

---

## 💡 Tips

### Configuration Priority
```
Code Defaults  →  config.yaml  →  Environment Variables
  (lowest)                          (highest priority)
```

### Testing Workflow
1. Configure test settings (short timeouts, no SSL verification)
2. Create test context with custom config
3. Run in preview mode to avoid sending emails
4. Check logs for errors

### Debugging Workflow
1. Enable DEBUG logging: `LOG_LEVEL=DEBUG`
2. Use BOTH output mode: `LOG_OUTPUT=both`
3. Run in preview mode
4. Review logs and email previews

---

## 🆘 Getting Help

If you can't find what you need:

1. **Check the main [docs README](../README.md)** - Navigation hub for all documentation
2. **Search [architecture docs](../architecture/)** - Technical details on components
3. **Enable debug logging** - See what's happening internally
4. **Use email preview mode** - Test without sending

---

**Last Updated:** June 17, 2026
