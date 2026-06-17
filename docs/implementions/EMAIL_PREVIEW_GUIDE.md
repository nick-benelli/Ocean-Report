# Email Preview System

## 📧 What It Does

When you run the report **without sending** (`run_email=False`), the system now:

1. ✅ **Prints to console** (as before)
2. ✅ **Saves HTML preview** - Open in browser to see formatted version
3. ✅ **Saves text preview** - Exact copy of what would be sent

## 📁 File Structure

```
logs/
└── email-previews/
    ├── email_preview_20260616_193709.html  # Browser-viewable version
    └── email_preview_20260616_193709.txt   # Plain text copy
```

**Note:** The entire `logs/` directory is gitignored, so these files **won't be committed**.

---

## 🎯 Why This Design?

### File Types Chosen:

| Format | Purpose | Why? |
|--------|---------|------|
| **HTML** | Visual preview | See exactly how it looks with formatting; Open in any browser |
| **Text** | Exact copy | This is the literal email content that gets sent |

### Location Chosen:

- `logs/email-previews/` keeps all temporary files organized
- Already gitignored (won't accidentally commit)
- Easy to clean up (`rm -rf logs/`)

### Naming Convention:

- `email_preview_YYYYMMDD_HHMMSS.*` - Timestamped
- Compare different runs side-by-side
- Sorted chronologically in file browser

---

## 🚀 How to Use

### Run Without Sending Email

```bash
uv run scripts/run_report_no_email.py
```

### Review the Output

**Option 1: Open HTML in Browser**
```bash
# macOS
open logs/email-previews/email_preview_*.html

# Linux
xdg-open logs/email-previews/email_preview_*.html

# Or just double-click the HTML file
```

**Option 2: View Plain Text**
```bash
cat logs/email-previews/email_preview_*.txt

# Or view the latest preview
cat $(ls -t logs/email-previews/*.txt | head -1)
```

---

## 📊 What the HTML Preview Includes

The HTML file shows:

1. **Preview Notice** - Yellow banner indicating this is a preview
2. **Email Headers** - To, BCC, From, Generated timestamp
3. **Subject Line** - Large and prominent
4. **Email Body** - Formatted with proper spacing
5. **Clean Layout** - Professional styling for easy reading

### Example Screenshot:

The HTML preview looks like this:
- Clean white background with subtle shadow
- Gray header box showing all recipients
- Large subject line
- Monospace font for the body (preserves formatting)
- Yellow notice banner at top

---

## 🛠️ Terminal Commands

### View Latest Preview Files

```bash
# List all previews
ls -lht logs/email-previews/

# View latest HTML in browser
open $(ls -t logs/email-previews/*.html | head -1)

# View latest text
cat $(ls -t logs/email-previews/*.txt | head -1)
```

### Compare Two Previews

```bash
# Compare the two most recent text previews
diff $(ls -t logs/email-previews/*.txt | sed -n '1p') \
     $(ls -t logs/email-previews/*.txt | sed -n '2p')
```

### Clean Up Old Previews

```bash
# Remove all previews
rm logs/email-previews/*

# Remove previews older than 7 days
find logs/email-previews -type f -mtime +7 -delete

# Remove all but the 5 most recent
ls -t logs/email-previews/email_preview_*.html | tail -n +6 | xargs rm
ls -t logs/email-previews/email_preview_*.txt | tail -n +6 | xargs rm
```

---

## ✨ Benefits

### 1. **Visual Confirmation**
- See exactly what recipients will see
- Catch formatting issues before sending
- Review emoji rendering

### 2. **Easy Comparison**
- Compare today's report vs yesterday's
- Track changes to email format
- Test different configurations

### 3. **Debugging**
- Plain text shows exact content
- HTML shows rendering issues
- Timestamped for tracking

### 4. **No Clutter**
- Automatically gitignored
- Organized in dedicated folder
- Easy to bulk delete

---

## 🔒 Security & Git

### Already Configured:

```gitignore
# .gitignore
logs/
```

This means:
- ✅ Email previews won't be committed
- ✅ Recipient email addresses stay private
- ✅ No sensitive data in version control

### Verify:

```bash
git status logs/
# Should show: nothing to commit, working tree clean
```

---

## 🎨 Customization

Want to change the preview styling? Edit the `_write_email_preview()` function in:
```
src/ocean_report/workflows/report_runner.py
```

Look for the `<style>` section to customize:
- Colors
- Fonts
- Layout
- Spacing

---

## 📝 Example Workflow

### 1. Test Your Email Format

```bash
# Run without sending
uv run scripts/run_report_no_email.py

# Review in browser
open logs/email-previews/email_preview_*.html
```

### 2. Make Changes

Edit formatting, content, or configuration...

### 3. Test Again

```bash
uv run scripts/run_report_no_email.py

# Compare with previous version
```

### 4. When Happy, Send It

```bash
# Edit script to enable email sending
uv run scripts/run_report.py  # or set RUN_EMAIL=True
```

---

## 🎓 What a Skilled Engineer Did Here

### Design Decisions:

1. **Two formats** (HTML + Text)
   - HTML: Visual confirmation
   - Text: Exact content verification

2. **Automatic timestamping**
   - No manual naming
   - Easy chronological sorting
   - Compare runs over time

3. **Proper location** (`logs/email-previews/`)
   - Organized and discoverable
   - Already gitignored
   - Easy to clean up

4. **User-friendly output**
   - Shows exact commands to run
   - Opens in default browser
   - Clear terminal feedback

5. **Security**
   - Gitignored by default
   - No risk of committing sensitive data

---

## 💡 Tips

### Quick Open Latest Preview

Add this to your `~/.zshrc` or `~/.bashrc`:

```bash
alias preview-email="open \$(ls -t logs/email-previews/*.html | head -1)"
```

Then just run:
```bash
preview-email
```

### Watch for Changes

```bash
# Auto-open new previews as they're created
fswatch -o logs/email-previews/*.html | xargs -n1 -I{} open {}
```

---

## 🎉 Summary

Every time you run the report without sending:
- ✅ Email printed to console
- ✅ HTML preview saved (open in browser)
- ✅ Text preview saved (exact copy)
- ✅ Files automatically timestamped
- ✅ Nothing committed to git
- ✅ Easy to review and compare
