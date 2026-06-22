#!/bin/bash
# preview-email-txt.sh - Displays the latest email preview (text) in the terminal

set -e

# Get the script directory and navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"

# Directory containing email previews
PREVIEW_DIR="logs/email-previews"

# Check if directory exists
if [ ! -d "$PREVIEW_DIR" ]; then
    echo "❌ Error: Email preview directory not found: $PREVIEW_DIR"
    echo "   Run the report first: uv run scripts/run_report_no_email.py"
    exit 1
fi

# Find the latest TXT preview file
LATEST_TXT=$(ls -t "$PREVIEW_DIR"/*.txt 2>/dev/null | head -1)

# Check if any TXT files exist
if [ -z "$LATEST_TXT" ]; then
    echo "❌ Error: No email preview files found in $PREVIEW_DIR"
    echo "   Run the report first: uv run scripts/run_report_no_email.py"
    exit 1
fi

# Get the filename for display
FILENAME=$(basename "$LATEST_TXT")

# Display the preview
echo "📧 Latest email preview: $FILENAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
cat "$LATEST_TXT"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ File: $LATEST_TXT"
