# Emailer Component

**Purpose**: Format ocean report data into human-readable emails and deliver them via SMTP.

**Location**: `src/ocean_report/emailer/`

---

## Overview

The Emailer component is responsible for the final step in the report workflow: taking raw data (water temperature, tides, wind) and transforming it into a nicely formatted email that gets delivered to subscribers.

### What It Does

**For Non-Technical Readers:**

Think of this component as the "presentation and delivery" layer. It takes technical data (numbers, timestamps, API responses) and turns it into an easy-to-read email like:

```
Daily Water Report – Monday, June 16, 2026

🌡️ Water Temperature: 72.5 °F

🌊 Tides:
High Tide at 7:32 AM — 3.1 ft
Low Tide at 1:45 PM — 0.8 ft

🌬️ Wind Forecast:
8 AM: 12 mph NW (Offshore) ⬇️
12 PM: 10 mph W (Cross-shore) ↔️
4 PM: 8 mph SW (Onshore) ⬆️
```

Then it sends this email to everyone on the subscriber list.

**For Technical Readers:**

- Plain-text email formatting with emoji icons for visual appeal
- Timezone-aware timestamp handling (UTC → Eastern Time)
- SMTP delivery with TLS encryption
- BCC support for privacy (recipients don't see each other)
- Optional preview mode (print to console instead of sending)

---

## Architecture

### File Structure

```
emailer/
├── __init__.py              # Public exports
├── email_formatter.py       # Converts data to email body text
├── sender.py                # SMTP delivery via smtplib
└── address_fetcher.py       # Fetches recipient lists from remote URLs
```

### Component Flow

```
┌──────────────┐
│  Raw Data    │  Water temp: 72.5, Tides: [...], Wind: [...]
└──────┬───────┘
       │
       ↓
┌──────────────────────────┐
│  email_formatter.py      │  Formats sections with emojis & labels
│  - format_water_temp()   │
│  - format_tide()          │
│  - format_wind_forecast() │
│  - generate_email_body()  │
└──────┬───────────────────┘
       │
       ↓
┌─────────────────┐
│  Email Body     │  "Daily Water Report – Monday..."
└──────┬──────────┘
       │
       ↓
┌──────────────────────────┐
│  sender.py               │  SMTP delivery
│  - send_email()          │
└──────────────────────────┘
       │
       ↓
┌──────────────────┐
│  Gmail SMTP      │
└──────────────────┘
```

---

## Core Components

### 1. Email Formatter (`email_formatter.py`)

**Purpose**: Convert ocean data into human-readable plain text.

#### Key Functions

##### `generate_email_body(sections, retrieval_timestamps) → str`

**What It Does**: Assembles the complete email body from pre-formatted sections.

**Example**:
```python
from ocean_report.emailer.email_formatter import generate_email_body

sections = [
    "🌡️ Water Temperature: 72.5 °F\n\n",
    "🌊 Tides:\nHigh Tide at 7:32 AM — 3.1 ft\n\n",
    "🌬️ Wind Forecast:\n8 AM: 12 mph NW (Offshore)\n\n"
]

timestamps = {
    "water_temp": datetime.now(),
    "tides": datetime.now(),
    "wind": datetime.now(),
}

body = generate_email_body(sections, timestamps)
print(body)
```

**Output**:
```
Daily Water Report – Monday, June 16, 2026 

🌡️ Water Temperature: 72.5 °F

🌊 Tides:
High Tide at 7:32 AM — 3.1 ft

🌬️ Wind Forecast:
8 AM: 12 mph NW (Offshore)

--------
Tide & water temp from NOAA (Atlantic City Station 8534720) | Wind by Open-Meteo

📊 Data Retrieved: Jun 16 at 6:45 AM
```

---

##### `format_water_temp(water_temperature) → str`

**What It Does**: Formats water temperature with emoji and units.

**Example**:
```python
from ocean_report.emailer.email_formatter import format_water_temp

# With data
result = format_water_temp(72.5)
# "🌡️ Water Temperature: 72.5 °F\n\n"

# Without data (None)
result = format_water_temp(None)
# "🌡️ Water Temperature: unavailable\n\n"
```

---

##### `format_tide(tides) → str`

**What It Does**: Formats tide predictions into readable text.

**Example**:
```python
from ocean_report.emailer.email_formatter import format_tide

tides = [
    {"type": "H", "t": "2026-06-16 07:32", "v": "3.1"},
    {"type": "L", "t": "2026-06-16 13:45", "v": "0.8"},
]

result = format_tide(tides)
```

**Output**:
```
🌊 Tides:
High Tide at 7:32 AM — 3.1 ft
Low Tide at 1:45 PM — 0.8 ft
```

---

##### `format_wind_forecast_email(wind_data) → str`

**What It Does**: Formats hourly wind forecast with direction arrows.

**Example**:
```python
from ocean_report.emailer.email_formatter import format_wind_forecast_email

wind_data = [
    {
        "time": "8 AM",
        "speed_mph": 12,
        "direction": "NW",
        "wind_type": "Offshore"
    },
    {
        "time": "12 PM",
        "speed_mph": 10,
        "direction": "W",
        "wind_type": "Cross-shore"
    }
]

result = format_wind_forecast_email(wind_data)
```

**Output**:
```
🌬️ Wind Forecast:
8 AM: 12 mph NW (Offshore) ⬇️
12 PM: 10 mph W (Cross-shore) ↔️
```

**Wind Type Indicators**:
- `⬇️` Offshore (good for surfing - clean waves)
- `⬆️` Onshore (choppy conditions)
- `↔️` Cross-shore (sideways wind)

---

### 2. Email Sender (`sender.py`)

**Purpose**: Deliver formatted emails via SMTP.

#### Key Function

##### `send_email(sender, password, recipients, bcc_recipients, subject, body, host, port) → None`

**What It Does**: Creates and sends an email using SMTP with STARTTLS encryption.

**Example**:
```python
from ocean_report.emailer.sender import send_email

send_email(
    sender="surf@example.com",
    password="app_password_123",
    recipients="primary@example.com",
    bcc_recipients="sub1@example.com,sub2@example.com",
    subject="Daily Water Report – Monday, June 16",
    body="🌡️ Water Temperature: 72.5 °F\n...",
    host="smtp.gmail.com",
    port=587
)
```

**What Happens Internally**:
1. Creates `MIMEText` message with UTF-8 encoding
2. Sets `From`, `To`, `Bcc`, `Subject` headers
3. Connects to SMTP server
4. Starts TLS encryption (`starttls()`)
5. Authenticates with username/password
6. Sends email to all recipients (To + Bcc)
7. Closes connection

**Security**:
- Uses `STARTTLS` for encryption
- Password should come from environment variable (not hardcoded)
- BCC used so recipients don't see each other's addresses

---

### 3. Address Fetcher (`address_fetcher.py`)

**Purpose**: Fetch recipient email lists from remote URLs (e.g., GitHub Gists).

**Why Remote URLs?**

Instead of hardcoding email lists in the codebase:
- Easy to update recipients without redeploying
- Can have seasonal lists (summer vs offseason)
- Keeps email addresses private (not in public repo)

#### Key Function

##### `get_recipients(use_url, fallback_recipients, test=False) → str`

**What It Does**: Fetches and normalizes a comma-separated list of email addresses.

**Example**:
```python
from ocean_report.emailer.address_fetcher import get_recipients

# Fetch from URL
recipients = get_recipients(
    use_url=True,
    fallback_recipients="backup@example.com",
    test=False
)
# Returns: "subscriber1@example.com,subscriber2@example.com,..."

# Use fallback (no URL)
recipients = get_recipients(
    use_url=False,
    fallback_recipients="user1@example.com,user2@example.com",
    test=False
)
# Returns: "user1@example.com,user2@example.com"
```

**Seasonal Logic**:
- Checks if today is in "summer" season (Memorial Day → Labor Day)
- Uses `main` URL during summer
- Uses `offseason` URL during offseason
- Uses `test` URL when `test=True`

**Normalization**:
- Converts all addresses to lowercase
- Removes duplicate addresses
- Returns comma-separated string

---

## Configuration

Emailer behavior is controlled by the `email:` section in `config.yaml`:

```yaml
email:
  smtp_server: smtp.gmail.com
  smtp_port: 587
  sender: ${EMAIL_ADDRESS}
  password: ${EMAIL_PASSWORD}
  recipients: ${EMAIL_RECIPIENTS}
  test_recipients: ${EMAIL_TEST_RECIPIENTS}
  use_recipient_url: true
  recipient_urls:
    main: ${MAIN_RECIPIENT_URL}
    test: ${TEST_RECIPIENT_URL}
    offseason: ${OFFSEASON_RECIPIENT_URL}
```

**Environment Variables**:
```bash
export EMAIL_ADDRESS="surf@example.com"
export EMAIL_PASSWORD="app_password_123"
export EMAIL_RECIPIENTS="backup1@example.com,backup2@example.com"
export MAIN_RECIPIENT_URL="https://gist.githubusercontent.com/.../main_recipients.txt"
```

---

## Usage Patterns

### Pattern 1: Full Workflow (Production)

```python
from ocean_report.emailer import generate_email_body, send_email, get_recipients

# 1. Format sections
sections = [
    format_water_temp(72.5),
    format_tide(tide_data),
    format_wind_forecast_email(wind_data),
]

# 2. Generate body
body = generate_email_body(sections, timestamps)

# 3. Get recipients
bcc_recipients = get_recipients(
    use_url=config.email.use_recipient_url,
    fallback_recipients=config.email.recipients,
    test=False
)

# 4. Send email
send_email(
    sender=config.email.sender,
    password=config.email.password,
    recipients=config.email.sender,  # Send to self in "To" field
    bcc_recipients=bcc_recipients,
    subject="Daily Water Report",
    body=body,
    host=config.email.smtp_server,
    port=config.email.smtp_port
)
```

---

### Pattern 2: Preview Mode (Testing)

```python
# Instead of sending, just print
body = generate_email_body(sections, timestamps)
print(body)
# No email sent - useful for testing formatting
```

---

### Pattern 3: Test Recipients

```python
# Send to test list instead of production list
bcc_recipients = get_recipients(
    use_url=config.email.use_recipient_url,
    fallback_recipients=config.email.test_recipients,
    test=True  # Uses test URL
)
```

---

## Design Decisions

### Decision: Plain Text Instead of HTML

**Chose**: Plain text with emoji

**Reasoning**:
- **Universally supported**: Works in all email clients
- **Accessible**: Screen readers handle plain text better
- **Simple**: No HTML/CSS maintenance
- **Fast to load**: No images, just text
- **Readable**: Emoji provide visual structure without complexity

---

### Decision: BCC Instead of Separate Emails

**Chose**: Single email with BCC

**Reasoning**:
- **Efficient**: One SMTP connection instead of hundreds
- **Private**: Recipients don't see each other
- **Fast**: Reduces email delivery time
- **Rate Limit Friendly**: Less likely to hit Gmail limits

---

### Decision: Emoji Icons

**Chose**: Use emoji (🌡️, 🌊, 🌬️)

**Reasoning**:
- **Visual**: Easy to scan email quickly
- **No Images Required**: Just Unicode characters
- **Universal**: Supported by all modern email clients
- **Personality**: Makes the email more engaging

---

## Testing Guidelines

### Unit Tests: Formatting

```python
def test_format_water_temp_with_value():
    result = format_water_temp(72.5)
    assert "72.5 °F" in result
    assert "🌡️" in result

def test_format_water_temp_without_value():
    result = format_water_temp(None)
    assert "unavailable" in result
```

---

### Integration Tests: SMTP

```python
@pytest.mark.integration
def test_send_email(test_config):
    # Send to test recipient
    send_email(
        sender=test_config.email.sender,
        password=test_config.email.password,
        recipients=test_config.email.test_recipients,
        bcc_recipients="",
        subject="Test Email",
        body="Test body",
        host=test_config.email.smtp_server,
        port=test_config.email.smtp_port
    )
    # No exception = success
```

---

## Common Issues

### Issue: SMTP Authentication Failed

**Symptom**: `SMTPAuthenticationError: Username and Password not accepted`

**Causes**:
1. Wrong password
2. Gmail: Need "App Password" (not regular password)
3. 2FA enabled without app password

**Solution**:
1. For Gmail: Generate App Password in Google Account settings
2. Use that password in `EMAIL_PASSWORD` environment variable

---

### Issue: Connection Timeout

**Symptom**: `SMTPServerDisconnected: Connection unexpectedly closed`

**Causes**:
1. Firewall blocking port 587
2. Wrong SMTP server hostname
3. Network connectivity issues

**Solution**:
1. Verify SMTP server and port in config
2. Test connectivity: `telnet smtp.gmail.com 587`
3. Check firewall rules

---

### Issue: Recipients Not Receiving Email

**Symptom**: No error, but recipients don't get email

**Causes**:
1. Email in spam folder
2. Invalid email addresses in BCC list
3. Gmail daily sending limit exceeded

**Solution**:
1. Check spam folders
2. Validate email address format
3. Check Gmail sending limits (500/day for free accounts)

---

## Related Components

- **[Workflows](./workflows.md)**: Orchestrates email generation and delivery
- **[Config](./config.md)**: Provides email settings (SMTP, recipients, etc.)
- **[Utils](./utils.md)**: Date utilities used for timestamp formatting

---

## Summary

**Key Takeaways**:

1. **Two Responsibilities**: Format data + Deliver email
2. **Plain Text**: Simple, accessible, universal
3. **BCC for Privacy**: Single email to many recipients
4. **Remote Recipient Lists**: Fetch from URLs for easy updates
5. **Timezone-Aware**: Converts UTC to Eastern Time for display

**When to Use**:
- At the end of the report workflow
- After all data has been fetched and processed
- For both preview (print) and production (send) modes

---

**Next**: See [Workflows](./workflows.md) to understand how emailer fits into the complete report generation process.
