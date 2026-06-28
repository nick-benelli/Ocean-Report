# Email Preview System Guide

## Overview

When you run the report **without sending** (`run_email=False`), the system generates three outputs so you can review the email before it's sent to recipients.

**What You Get:**
1. ✅ **Console output** - Printed to terminal (as before)
2. ✅ **HTML preview** - Open in browser to see formatted version
3. ✅ **Text preview** - Exact copy of what would be sent

---

## Quick Reference

### Run Without Sending

```bash
uv run scripts/run_report_no_email.py
```

### View Latest HTML Preview

```bash
# macOS
open logs/email-previews/email_preview_*.html

# Linux
xdg-open logs/email-previews/email_preview_*.html
```

### View Latest Text Preview

```bash
cat $(ls -t logs/email-previews/*.txt | head -1)
```

### Clean Up Old Previews

```bash
rm logs/email-previews/*
```

---

## File Structure

```
logs/
└── email-previews/
    ├── email_preview_20260616_193709.html  # Browser-viewable version
    ├── email_preview_20260616_193709.txt   # Plain text copy
    ├── email_preview_20260617_093015.html
    └── email_preview_20260617_093015.txt
```

**Note:** The entire `logs/` directory is gitignored, so these files **won't be committed** to version control.

---

## File Types Explained

| Format | Purpose | Why? |
|--------|---------|------|
| **HTML** | Visual preview | See exactly how it looks with formatting; Open in any browser |
| **Text** | Exact copy | This is the **literal email content** that gets sent |

### HTML Preview Features:
- Clean white background with subtle shadow
- Gray header box showing all recipients
- Large subject line
- Monospace font for the body (preserves formatting)
- Yellow "PREVIEW" notice banner at top
- Professional styling for easy reading

### Text Preview:
- Identical to what recipients receive
- Plain text with emoji
- No HTML formatting
- Copy/paste friendly

---

## Design Rationale

### Location: `logs/email-previews/`

**Why this location?**
- ✅ Keeps all temporary files organized
- ✅ Already gitignored (won't accidentally commit)
- ✅ Easy to clean up (`rm -rf logs/`)
- ✅ Separate from other logs (runs, reports)

---

### Naming: `email_preview_YYYYMMDD_HHMMSS.*`

**Why timestamped?**
- ✅ Compare different runs side-by-side
- ✅ Sorted chronologically in file browser
- ✅ Easy to identify when each preview was created
- ✅ No name conflicts when running multiple times

---

## Usage Examples

### Example 1: Quick Preview in Terminal

```bash
# Run report without sending
uv run scripts/run_report_no_email.py

# Output shows in console immediately
```

**Console Output:**
```
========================================
EMAIL PREVIEW
========================================
Subject: Daily Water Report – Tuesday, June 17, 2026
To: surf@example.com
BCC: [15 recipients]
========================================

Daily Water Report – Tuesday, June 17, 2026

🌡️ Water Temperature: 72.5 °F
Updated at: 8:30 AM (Data from: 8:00 AM)

🌊 Tides:
High Tide at 7:32 AM — 3.1 ft
Low Tide at 1:45 PM — 0.8 ft

🌬️ Wind Forecast:
8 AM: 12 mph NW (Offshore)
12 PM: 10 mph W (Cross-shore)
4 PM: 8 mph SW (Onshore)

========================================
```

---

### Example 2: Open HTML in Browser

```bash
# Run report
uv run scripts/run_report_no_email.py

# Open latest HTML preview
open $(ls -t logs/email-previews/*.html | head -1)
```

**Browser shows:**
- Professional email layout
- "PREVIEW - NOT SENT" banner in yellow
- Email headers (To, BCC, From, Generated timestamp)
- Formatted body with proper spacing
- Easy to read and review

---

### Example 3: Review Text Copy

```bash
# View exact text that would be sent
cat logs/email-previews/email_preview_*.txt
```

This is **exactly** what recipients would receive in their inbox.

---

### Example 4: Compare Two Runs

```bash
# Compare the two most recent text previews
diff $(ls -t logs/email-previews/*.txt | sed -n '1p') \
     $(ls -t logs/email-previews/*.txt | sed -n '2p')
```

**Use when:**
- Testing configuration changes
- Verifying data updates
- Checking format modifications

---

### Example 5: Archive a Preview

```bash
# Save a specific preview for later reference
cp logs/email-previews/email_preview_20260617_093015.html \
   ~/Documents/ocean-report-baseline.html
```

---

## Terminal Commands

### List All Previews

```bash
# List all previews (newest first)
ls -lht logs/email-previews/

# Count preview files
ls logs/email-previews/*.html | wc -l
```

---

### View Latest Preview

```bash
# HTML in browser
open $(ls -t logs/email-previews/*.html | head -1)

# Text in terminal
cat $(ls -t logs/email-previews/*.txt | head -1)

# Text with paging
less $(ls -t logs/email-previews/*.txt | head -1)
```

---

### Compare Previews

```bash
# Compare two most recent
diff $(ls -t logs/email-previews/*.txt | sed -n '1p') \
     $(ls -t logs/email-previews/*.txt | sed -n '2p')

# Compare specific previews
diff logs/email-previews/email_preview_20260616_193709.txt \
     logs/email-previews/email_preview_20260617_093015.txt
```

---

### Clean Up Previews

```bash
# Remove all previews
rm logs/email-previews/*

# Remove previews older than 7 days
find logs/email-previews -type f -mtime +7 -delete

# Keep only the 5 most recent
ls -t logs/email-previews/email_preview_*.html | tail -n +6 | xargs rm
ls -t logs/email-previews/email_preview_*.txt | tail -n +6 | xargs rm

# Remove all but today's previews
find logs/email-previews -type f ! -name "*$(date +%Y%m%d)*" -delete
```

---

### Batch Operations

```bash
# Count total previews
echo "Total previews: $(ls logs/email-previews/*.html | wc -l)"

# Show disk usage
du -sh logs/email-previews/

# Find previews from specific date
ls logs/email-previews/*20260617*.html
```

---

## Benefits

### 1. Visual Confirmation
- ✅ See exactly what recipients will see
- ✅ Catch formatting issues before sending
- ✅ Review emoji rendering
- ✅ Verify subject line and recipients

---

### 2. Easy Comparison
- ✅ Compare today's report vs yesterday's
- ✅ Track changes to email format
- ✅ Test different configurations
- ✅ Verify data updates

---

### 3. Debugging
- ✅ Plain text shows exact content
- ✅ HTML shows rendering issues
- ✅ Timestamped for tracking
- ✅ Easy to share with team

---

### 4. No Clutter
- ✅ Automatically gitignored
- ✅ Organized in dedicated folder
- ✅ Easy to bulk delete
- ✅ Separate from other logs

---

## Security & Privacy

### Gitignore Configuration

The `logs/` directory is already gitignored:

```gitignore
# .gitignore
logs/
```

**This means:**
- ✅ Email previews won't be committed to version control
- ✅ Recipient email addresses stay private
- ✅ No sensitive data in Git history

---

### Verify Gitignore

```bash
# Check that logs/ is ignored
git status logs/
# Should show: nothing to commit, working tree clean

# Verify files aren't tracked
git ls-files logs/
# Should show: (empty)
```

---

### Best Practices

1. **Don't commit preview files**
   - Already handled by `.gitignore`
   - Double-check before force-adding files

2. **Clean up old previews regularly**
   ```bash
   # Weekly cleanup (crontab example)
   0 2 * * 0 find /path/to/Ocean-Report/logs/email-previews -type f -mtime +14 -delete
   ```

3. **Be careful sharing preview files**
   - May contain recipient email addresses
   - May contain sensitive report data
   - Redact before sharing externally

---

## Customization

### Modify Preview HTML Styling

The preview HTML is generated in `src/ocean_report/workflows/report_runner.py`:

```python
def _write_email_preview(subject, body, to, bcc, from_addr):
    """Write email preview to HTML and text files."""
    # ... implementation ...
```

**To customize:**
1. Edit the `<style>` section in the HTML template
2. Change colors, fonts, layout, spacing
3. Add additional metadata or information
4. Modify the preview banner styling

**Example customizations:**
- Change banner color from yellow to blue
- Add timestamp in a different format
- Include configuration details in preview
- Add links to related files

---

### Change Preview Location

To save previews in a different location, modify the `preview_dir` in `report_runner.py`:

```python
# Current
preview_dir = Path("logs/email-previews")

# Custom
preview_dir = Path("previews")  # Save in top-level previews/ folder
```

---

## Example Workflow

### Daily Development Routine

```bash
# 1. Make changes to code or config
vim src/ocean_report/emailer/template_renderer.py

# 2. Generate preview
uv run scripts/run_report_no_email.py

# 3. Review in browser
open $(ls -t logs/email-previews/*.html | head -1)

# 4. If looks good, compare with previous
diff $(ls -t logs/email-previews/*.txt | sed -n '2p') \
     $(ls -t logs/email-previews/*.txt | sed -n '1p')

# 5. When satisfied, send for real
uv run scripts/run_report.py
```

---

### Testing Different Configurations

```bash
# Test default config
uv run scripts/run_report_no_email.py
mv logs/email-previews/email_preview_*.html preview_default.html

# Test custom config
OCEAN_REPORT_CONFIG=configs/custom.yaml uv run scripts/run_report_no_email.py
mv logs/email-previews/email_preview_*.html preview_custom.html

# Compare in browser
open preview_default.html preview_custom.html
```

---

### Pre-Production Checklist

Before sending to real recipients:

```bash
# 1. Generate preview
uv run scripts/run_report_no_email.py

# 2. Review HTML
open $(ls -t logs/email-previews/*.html | head -1)

# 3. Check for issues:
#    - Subject line correct?
#    - Recipients list correct?
#    - Data looks reasonable?
#    - No errors or missing data?
#    - Formatting looks good?

# 4. If all good, send it!
uv run scripts/run_report.py
```

---

## Troubleshooting

### Preview Files Not Created

**Check:**
1. **Running in preview mode?**
   ```bash
   uv run scripts/run_report_no_email.py  # ✅
   uv run scripts/run_report.py  # ❌ (sends email, no preview)
   ```

2. **Directory exists?**
   ```bash
   ls -la logs/email-previews/  # Should exist
   ```

3. **Permissions?**
   ```bash
   ls -ld logs/email-previews/
   # Should show: drwxr-xr-x (read/write)
   ```

---

### HTML Not Opening in Browser

**Try:**
```bash
# Explicit browser command
/Applications/Safari.app/Contents/MacOS/Safari logs/email-previews/email_preview_*.html

# Or use default browser
open -a "Google Chrome" logs/email-previews/email_preview_*.html
```

---

### Old Previews Taking Up Space

**Check disk usage:**
```bash
du -sh logs/email-previews/
```

**Clean up:**
```bash
# Keep only last 10 previews
ls -t logs/email-previews/*.html | tail -n +11 | xargs rm
ls -t logs/email-previews/*.txt | tail -n +11 | xargs rm
```

---

## See Also

- [Emailer Component](../architecture/emailer.md) - Email formatting and sending
- [Workflows](../architecture/workflows.md) - How preview fits into the workflow
- [Configuration Setup](./config-setup.md) - Configuring email settings
