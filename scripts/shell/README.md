# Utility Scripts

Helper scripts for Ocean Report development and operations.

## 📧 Email Preview

### preview-email.sh
Opens the latest email preview (HTML) in your browser.

```bash
./help/bin/preview-email.sh
```

**What it does:**
- Finds the most recent HTML preview in `logs/email-previews/`
- Opens it in your default browser
- Shows helpful error messages if no previews exist

### preview-email-txt.sh
Displays the latest email preview (text) in your terminal.

```bash
./help/bin/preview-email-txt.sh
```

**What it does:**
- Finds the most recent text preview in `logs/email-previews/`
- Displays it directly in your terminal with nice formatting
- Shows the exact email content that would be sent

---

## 🧹 Cache Management

### clear-cache.sh
Clears Python cache files and build artifacts.

```bash
./help/bin/clear-cache.sh
```

---

## 🏃 Package Execution

### run-package.sh
Runs the ocean-report package directly.

```bash
./help/bin/run-package.sh
```

---

## 🌳 Project Structure

### tree-view.sh
Displays the project directory structure.

```bash
./help/bin/tree-view.sh
```

---

## 💡 Tips

### Run from anywhere in the project

These scripts automatically find the project root, so you can run them from any directory:

```bash
# From project root
./help/bin/preview-email.sh

# From subdirectory
../../help/bin/preview-email.sh

# Or add to your PATH
export PATH="$PATH:$HOME/path/to/Ocean-Report/help/bin"
preview-email.sh
```

### Make scripts globally accessible

Add this to your `~/.zshrc`:

```bash
# Ocean Report utilities
export PATH="$PATH:$HOME/Workspace/repos/GitHub/Ocean-Report/help/bin"
```

Then reload:
```bash
source ~/.zshrc
```

Now you can run from anywhere:
```bash
preview-email.sh
preview-email-txt.sh
clear-cache.sh
tree-view.sh
```

---

## 🛠️ Script Development

All scripts follow these conventions:

1. **Shebang:** `#!/bin/bash`
2. **Set options:** `set -e` (exit on error)
3. **Find project root:** Navigate relative to script location
4. **Error handling:** Helpful messages with emoji
5. **Executable:** `chmod +x script.sh`

---

## 📝 Adding New Scripts

1. Create script in `help/bin/`
2. Make it executable: `chmod +x help/bin/your-script.sh`
3. Add documentation to this README
4. Test from different directories
