#!/bin/bash
# preview-email.sh - Opens the latest email preview in your browser

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

# Find the latest HTML preview file
LATEST_HTML=$(ls -t "$PREVIEW_DIR"/*.html 2>/dev/null | head -1)

# Check if any HTML files exist
if [ -z "$LATEST_HTML" ]; then
    echo "❌ Error: No email preview files found in $PREVIEW_DIR"
    echo "   Run the report first: uv run scripts/run_report_no_email.py"
    exit 1
fi

# Get the filename for display
FILENAME=$(basename "$LATEST_HTML")

# Open the latest preview
echo "📧 Opening latest email preview: $FILENAME"
open "$LATEST_HTML"

echo "✅ Email preview opened in your default browser"
