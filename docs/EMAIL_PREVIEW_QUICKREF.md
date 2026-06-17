# Email Preview System - Quick Reference

## 🎯 What You Get

When running without sending email, you now get **three outputs**:

1. **Console** - Printed to terminal (as before)
2. **HTML File** - Open in browser to see formatted preview
3. **Text File** - Exact copy of email content

---

## 📁 Location

```
logs/email-previews/
├── email_preview_20260616_193709.html  ← Open in browser
└── email_preview_20260616_193709.txt   ← Exact copy
```

✅ **Gitignored** - Won't be committed to version control

---

## 🚀 Quick Commands

### Run Without Sending
```bash
uv run scripts/run_report_no_email.py
```

### Open Latest HTML Preview
```bash
open logs/email-previews/email_preview_*.html
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

## 💡 Why These File Types?

| Format | Purpose |
|--------|---------|
| **HTML** | Visual preview - See formatting, colors, layout |
| **Text** | Exact copy - This is literally what gets sent |

---

## 🎓 What Changed

**Modified:**
- [.gitignore](.gitignore) - Added `logs/` to ignore email previews
- [report_runner.py](src/ocean_report/workflows/report_runner.py) - Added `_write_email_preview()` function

**Created:**
- [EMAIL_PREVIEW_GUIDE.md](docs/EMAIL_PREVIEW_GUIDE.md) - Complete documentation

---

## ✅ Verified

- ✅ Files created with timestamp
- ✅ HTML opens in browser
- ✅ Text file is exact copy
- ✅ Files gitignored (won't commit)
- ✅ Organized in dedicated directory

---

**Read more:** [EMAIL_PREVIEW_GUIDE.md](docs/EMAIL_PREVIEW_GUIDE.md)
