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
├── __init__.py                  # Public exports (currently empty)
├── template_renderer.py         # Jinja2 template rendering
├── template_helpers.py          # Data formatting helpers for templates
├── template_html_helpers.py     # HTML formatting helpers
├── sender.py                    # SMTP delivery via smtplib
└── address_fetcher.py           # Fetches recipient lists from remote URLs
```

### Component Flow

```
┌──────────────┐
│  Raw Data    │  Water temp: 72.5, Tides: [...], Wind: [...]
└──────┬───────┘
       │
       ↓
┌──────────────────────────┐
│  template_helpers.py     │  Format individual values
│  - format_water_temp_value()
│  - format_tide_info()    │
│  - format_wind_info()    │
└──────┬───────────────────┘
       │
       ↓
┌──────────────────────────┐
│  EmailTemplateData       │  Structured data model
│  (models/email.py)       │
└──────┬───────────────────┘
       │
       ↓
┌──────────────────────────┐
│  template_renderer.py    │  Jinja2 rendering
│  - render_email_template()
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

### 1. Template Renderer (`template_renderer.py`)

**Purpose**: Render email body from Jinja2 templates with structured data.

#### Key Functions

##### `render_email_template(data, template_path=None) → str`

**What It Does**: Renders email body from Jinja2 template using `EmailTemplateData`.

**Example**:
```python
from ocean_report.emailer.template_renderer import render_email_template
from ocean_report.models.email import EmailTemplateData

data = EmailTemplateData(
    long_date="Monday, June 16, 2026",
    water_temp="72.5 °F",
    tide_info="⬇️ Low Tide at 8:23 AM — 0.3 ft\n⬆️ High Tide at 2:46 PM — 4.1 ft",
    wind_info="•  8 AM:  4.8 mph ESE (108.0°) → Cross/Onshore",
    station_name="Atlantic City Station 8534720",
    station_city="Atlantic City",
    wind_provider="Open-Meteo",
    date_retrieved="Jun 16 at 6:45 AM",
    water_temp_measured_at_date="Jun 16 at 6:30 AM"
)

body = render_email_template(data)
print(body)
```

**Features**:
- Jinja2 templating with auto-escaping disabled (plain text)
- Trim blocks and lstrip blocks for clean output
- Template path from config or custom path
- Validates template file exists before rendering

---

### 2. Template Helpers (`template_helpers.py`)

**Purpose**: Format individual data values for template consumption (NOT complete sections).

#### Key Functions

##### `format_water_temp_value(water_temperature) → str | None`

**What It Does**: Formats water temperature value with units.

**Example**:
```python
from ocean_report.emailer.template_helpers import format_water_temp_value

# With data
result = format_water_temp_value(72.5)
# "72.5 °F"

# Without data (None)
result = format_water_temp_value(None)
# "Unavailable ⚠️"
```

---

##### `format_tide_info(tide_events) → str | None`

**What It Does**: Formats tide predictions as multi-line string.

**Example**:
```python
from ocean_report.emailer.template_helpers import format_tide_info

tides = [
    NoaaTidePredictionRecord(timestamp="2026-06-16 07:32", event_type="H", height_feet="3.1"),
    NoaaTidePredictionRecord(timestamp="2026-06-16 13:45", event_type="L", height_feet="0.8"),
]

result = format_tide_info(tides)
```

**Output**:
```
• ⬆️ High Tide at 7:32 AM — 3.1 ft
• ⬇️ Low Tide at 1:45 PM — 0.8 ft
```

---

##### `format_wind_info(wind_data) → str | None`

**What It Does**: Formats hourly wind forecast as multi-line string.

**Example**:
```python
from ocean_report.emailer.template_helpers import format_wind_info

wind_data = [
    {"time": "8 AM", "speed_mph": 12.0, "direction": "NW", 
     "direction_deg": 315.0, "wind_type": "Offshore"},
]

result = format_wind_info(wind_data)
```

**Output**:
```
•  8 AM: 12.0 mph NW  (315.0°) → Offshore
```

---

##### `format_retrieval_timestamp(retrieval_time) → str`

**What It Does**: Formats data retrieval timestamp to Eastern Time.

**Example**:
```python
from ocean_report.emailer.template_helpers import format_retrieval_timestamp

timestamp = datetime.now(timezone.utc)
result = format_retrieval_timestamp(timestamp)
# "Jun 16 at 6:45 AM"
```

---

##### `format_long_date(date=None) → str`

**What It Does**: Formats date as long format for email header.

**Example**:
```python
from ocean_report.emailer.template_helpers import format_long_date

result = format_long_date()
# "Monday, June 16, 2026"
```

---

### 3. Email Sender (`sender.py`)

**Purpose**: Deliver formatted emails via SMTP.

#### EmailRecipients Dataclass

```python
@dataclass(frozen=True)
class EmailRecipients:
    """Container for primary and BCC recipients."""
    to_email: str = ""
    bcc_list: List[str] = field(default_factory=list)
```

#### Key Function

##### `send_email(subject, body, sender_email, email_password, recipients, smtp_server, smtp_port) → None`

**What It Does**: Creates and sends an email using SMTP with STARTTLS encryption.

**Example**:
```python
from ocean_report.emailer.sender import send_email, EmailRecipients

send_email(
    subject="Daily Water Report",
    body="Here is today's report...",
    sender_email="surf@example.com",
    email_password="app_password_123",
    recipients=EmailRecipients(
        to_email="",  # Empty for BCC-only
        bcc_list=["user1@example.com", "user2@example.com"]
    ),
    smtp_server="smtp.gmail.com",
    smtp_port=587
)
```

**What Happens Internally**:
1. Validates email password is provided
2. Creates `MIMEText` message with UTF-8 encoding
3. Sets `From`, `To`, `Bcc`, `Subject` headers
4. Connects to SMTP server
5. Starts TLS encryption (`starttls()`)
6. Authenticates with username/password
7. Sends email to all recipients (To + Bcc)
8. Closes connection

**Security**:
- Uses `STARTTLS` for encryption
- Password should come from environment variable (not hardcoded)
- BCC used so recipients don't see each other's addresses

---

### 4. Address Fetcher (`address_fetcher.py`)

**Purpose**: Fetch recipient email lists from remote URLs (e.g., GitHub Gists).

**Why Remote URLs?**

Instead of hardcoding email lists in the codebase:
- Easy to update recipients without redeploying
- Can have seasonal lists (summer vs offseason)
- Keeps email addresses private (not in public repo)

#### Key Functions

##### `fetch_recipients_from_gist(client, url) → str`

**What It Does**: Fetches raw email recipient list from a public Gist URL.

**Example**:
```python
from ocean_report.emailer.address_fetcher import fetch_recipients_from_gist
from ocean_report.api_client.client import ApiClient

client = ApiClient()
raw_text = fetch_recipients_from_gist(
    client=client,
    url="https://gist.githubusercontent.com/.../recipients.txt"
)
# Returns: "email1@example.com,email2@example.com\nuser3@example.com"
```

---

##### `parse_recipients(text, verbose=False) → str`

**What It Does**: Cleans and normalizes a comma-separated list of email addresses.

**Example**:
```python
from ocean_report.emailer.address_fetcher import parse_recipients

raw_text = """
subscriber1@example.com,
subscriber2@example.com
user3@example.com
"""

recipients = parse_recipients(raw_text)
# Returns: "subscriber1@example.com,subscriber2@example.com,user3@example.com"
```

**Normalization**:
- Converts all addresses to lowercase
- Replaces commas with newlines for splitting
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

### Pattern 1: Full Workflow (Template-Based)

```python
from ocean_report.emailer.template_renderer import render_email_template
from ocean_report.emailer.sender import send_email, EmailRecipients
from ocean_report.models.email import EmailTemplateData

# 1. Create template data model
email_data = EmailTemplateData(
    long_date="Monday, June 16, 2026",
    water_temp="72.5 °F",
    tide_info="⬇️ Low Tide at 8:23 AM — 0.3 ft\n⬆️ High Tide at 2:46 PM — 4.1 ft",
    wind_info="•  8 AM:  4.8 mph ESE (108.0°) → Cross/Onshore",
    station_name="Atlantic City Station 8534720",
    station_city="Atlantic City",
    wind_provider="Open-Meteo",
    date_retrieved="Jun 16 at 6:45 AM",
    water_temp_measured_at_date="Jun 16 at 6:30 AM"
)

# 2. Render template
body = render_email_template(email_data)

# 3. Send email
send_email(
    subject="Daily Water Report",
    body=body,
    sender_email="surf@example.com",
    email_password="app_password_123",
    recipients=EmailRecipients(
        to_email="",
        bcc_list=["user1@example.com", "user2@example.com"]
    ),
    smtp_server="smtp.gmail.com",
    smtp_port=587
)
```

---

### Pattern 2: Preview Mode (Testing)

```python
from ocean_report.emailer.template_renderer import render_email_template

# Render and print without sending
body = render_email_template(email_data)
print(body)
# No email sent - useful for testing formatting
```

---

### Pattern 3: Custom Template

```python
from pathlib import Path

# Use custom template instead of config default
body = render_email_template(
    email_data,
    template_path=Path("templates/custom_report.txt.jinja")
)
```

---

### Pattern 4: Fetching Recipients from URL

```python
from ocean_report.emailer.address_fetcher import (
    fetch_recipients_from_gist,
    parse_recipients
)
from ocean_report.api_client.client import ApiClient

# Fetch from remote URL
client = ApiClient()
raw_text = fetch_recipients_from_gist(
    client=client,
    url="https://gist.githubusercontent.com/.../recipients.txt"
)

# Parse and normalize
recipients_str = parse_recipients(raw_text)
recipient_list = [email.strip() for email in recipients_str.split(",")]
```

---

## Design Decisions

### Decision: Jinja2 Templates Instead of String Formatting

**Chose**: Jinja2 templates with structured data models

**Reasoning**:
- **Separation of Concerns**: Template designers can modify layout without touching Python code
- **Type Safety**: `EmailTemplateData` model validates data before rendering
- **Testability**: Can test data formatting separately from template rendering
- **Flexibility**: Easy to create multiple email formats (HTML, plain text, etc.)
- **Professional**: Industry-standard templating engine

---

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

### Unit Tests: Template Helpers

```python
from ocean_report.emailer.template_helpers import format_water_temp_value

def test_format_water_temp_with_value():
    result = format_water_temp_value(72.5)
    assert result == "72.5 °F"

def test_format_water_temp_none():
    result = format_water_temp_value(None)
    assert "Unavailable" in result
```

### Unit Tests: Template Rendering

```python
from ocean_report.emailer.template_renderer import render_email_template
from ocean_report.models.email import EmailTemplateData

def test_render_email_template():
    data = EmailTemplateData(
        long_date="Monday, June 16, 2026",
        water_temp="72.5 °F",
        tide_info="Tide data here",
        wind_info="Wind data here",
        station_name="Test Station",
        station_city="Test City",
        wind_provider="Test Provider",
        date_retrieved="Jun 16 at 6:45 AM",
        water_temp_measured_at_date=None
    )
    
    body = render_email_template(data)
    
    assert "Monday, June 16, 2026" in body
    assert "72.5 °F" in body
    assert "Test Station" in body
```

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
