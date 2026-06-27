# Configuration Files

This directory contains configuration files for the Ocean Report application.

## Quick Start

### Option 1: Use Environment Variables (Recommended for Security)

1. **Use the existing config.yaml** (already uses environment variables):
   ```bash
   export EMAIL_SENDER="your-email@gmail.com"
   export EMAIL_PASSWORD="your-app-password"
   export RECIPIENTS_GIST_URL="https://gist.githubusercontent.com/..."
   # ... set other required variables
   ```

2. **Run the application**:
   ```bash
   ocean-report run
   ```

### Option 2: Create a Local Config

1. **Copy the template**:
   ```bash
   cp config.template.yaml config.local.yaml
   ```

2. **Edit `config.local.yaml`** and replace `${VARIABLES}` with actual values

3. **Run with your local config**:
   ```bash
   ocean-report run --config configs/config.local.yaml
   ```

**Note**: `*.local.yaml` files are gitignored, so your credentials stay private!

## Configuration Files

### `config.template.yaml` ⭐
**Purpose**: Comprehensive template with full documentation

- Extensive comments explaining every option
- Example values and recommendations
- Configuration tips and best practices
- **Copy this** to create your own config

### `config.yaml`
**Purpose**: Default configuration using environment variables

- Uses `${VARIABLE}` syntax for all sensitive data
- Safe to commit (no credentials stored)
- **This is the working default** - set environment variables to use it
- Tracked in git for team sharing

### `config.local.yaml` (you create this)
**Purpose**: Your personal local configuration

- **Gitignored** - never committed
- Replace `${VARIABLES}` with real values
- Best for local development with hardcoded settings
- Create from template: `cp config.template.yaml config.local.yaml`

### `config_with_logging.yaml`
**Purpose**: Example showing file-based logging

- Demonstrates logging configuration options
- Reference for debugging setups
- Tracked in git as an example

## Environment Variables

The application supports environment variables for sensitive data and deployment-specific settings.

### Required Variables

```bash
# Email credentials
export EMAIL_SENDER="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-specific-password"

# Location (if using environment variables)
export LONGITUDE="-74.2"
export LATITUDE="39.5"
```

### Optional Variables

```bash
# Recipient management (if using URL-based recipients)
export RECIPIENTS_GIST_URL="https://gist.githubusercontent.com/..."
export TEST_RECIPIENTS_GIST_URL="https://gist.githubusercontent.com/..."
export OFFSEASON_RECIPIENTS_GIST_URL="https://gist.githubusercontent.com/..."

# Or direct recipient lists
export EMAIL_RECIPIENTS="user1@example.com,user2@example.com"
export TEST_RECIPIENTS="test@example.com"

# Logging configuration
export LOG_OUTPUT="console"  # or "file" or "both"
export LOG_FILE_PATH="logs/ocean_report.log"
export LOG_LEVEL="INFO"  # or DEBUG, WARNING, ERROR, CRITICAL
```

## Gmail App Passwords

If using Gmail, you need an app-specific password (not your regular password):

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification (if not already enabled)
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Generate a new app password for "Mail"
5. Use this 16-character password as `EMAIL_PASSWORD`

## URL-Based Recipient Lists

For managing multiple recipients, use GitHub Gists:

1. Create a new Gist at https://gist.github.com/
2. Add one email address per line:
   ```
   user1@example.com
   user2@example.com
   user3@example.com
   ```
3. Click "Create secret gist" or "Create public gist"
4. Click the "Raw" button and copy the URL
5. Use this URL in your config:
   ```yaml
   recipient_urls:
     main: "https://gist.githubusercontent.com/username/abc123/raw/..."
   ```

## Multiple Environments

You can create different configs for different environments:

```bash
configs/
├── config.template.yaml        # Template (tracked in git) ⭐
├── config.yaml                 # Default with env vars (tracked in git)
├── config.local.yaml           # Your local config (gitignored)
├── config.dev.yaml             # Development (gitignored)
├── config.test.yaml            # Testing (gitignored)
├── config.prod.yaml            # Production (gitignored)
└── config_with_logging.yaml    # Logging example (tracked in git)
```

**Patterns that are gitignored**:
- `*.local.yaml` - Local development configs
- `config.dev.yaml` - Development environment
- `config.test.yaml` - Testing environment
- `config.prod.yaml` - Production environment

Load a specific config:
```python
from ocean_report.config import load_config
config = load_config("configs/config.dev.yaml")
```

Or via command line:
```bash
ocean-report run --config configs/config.dev.yaml
```

## Configuration Reference

See [`config.template.yaml`](config.template.yaml) for detailed documentation of all configuration options.

### Key Sections

- **noaa**: Station IDs for data sources
- **email**: SMTP settings and recipients
- **location**: Beach coordinates and orientation
- **reporting**: Email template and subject customization
- **summer**: Season date calculations
- **api**: HTTP client behavior
- **logging**: Output and verbosity settings

## Security Best Practices

1. ✅ **Use environment variables** for secrets (passwords, API keys)
2. ✅ **Never commit** `config.yaml` with real credentials
3. ✅ **Use app-specific passwords** for email (not your account password)
4. ✅ **Rotate credentials** periodically
5. ✅ **Use `.env` files** for local development (also gitignored)

## Troubleshooting

### Config not found
```
Error: Configuration file not found
```
**Solution**: Create `config.yaml` from the template

### SSL Certificate errors
```
SSL: CERTIFICATE_VERIFY_FAILED
```
**Solution**: Set `api.verify_ssl: false` or fix your system certificates

### Email authentication failed
```
Authentication failed
```
**Solution**: Use an app-specific password, not your regular Gmail password

### Environment variables not resolving
```
Invalid value: ${EMAIL_SENDER}
```
**Solution**: Export the environment variable or replace with a direct value

## Need Help?

- Check [`config.template.yaml`](config.template.yaml) for detailed comments
- See the [main README](../README.md) for setup instructions
- Review [architecture docs](../docs/architecture/) for configuration schema details
