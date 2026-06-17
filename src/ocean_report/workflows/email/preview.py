"""Email preview utility for ocean report workflows."""
from pathlib import Path
from datetime import datetime


def write_email_preview(
    subject: str,
    body: str,
    sender_email: str,
    email_recipients: str,
    bcc_recipients: list[str],
) -> Path:
    """Write email preview to files for review.
    
    Creates both HTML and plain text versions in logs/email-previews/
    with timestamped filenames.
    
    Args:
        subject: Email subject line
        body: Email body content
        sender_email: Sender email address
        email_recipients: To: recipients
        bcc_recipients: BCC recipients list
        
    Returns:
        Path to the HTML preview file
    """
    # Create preview directory
    preview_dir = Path("logs/email-previews")
    preview_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"email_preview_{timestamp}"

    # Prepare email header info
    header_text = (
        f"To: {email_recipients}\n"
        f"BCC: {', '.join(bcc_recipients)}\n"
        f"From: {sender_email}\n\n"
        f"Subject: {subject}\n\n"
    )

    # Write plain text version (exact copy of what would be sent)
    txt_file = preview_dir / f"{base_filename}.txt"
    txt_file.write_text(header_text + body, encoding="utf-8")

    # Write HTML version (formatted for browser viewing)
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .email-container {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        .email-header {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            font-size: 0.9em;
            color: #666;
        }}
        .email-header div {{
            margin: 5px 0;
        }}
        .email-header strong {{
            color: #333;
        }}
        .email-subject {{
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 20px;
            color: #1a1a1a;
        }}
        .email-body {{
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            line-height: 1.6;
            color: #333;
        }}
        .preview-notice {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 12px;
            margin-bottom: 20px;
            border-radius: 4px;
        }}
        .preview-notice strong {{
            color: #856404;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="preview-notice">
            <strong>📧 Email Preview</strong> — This is how your email will appear to recipients
        </div>

        <div class="email-header">
            <div><strong>To:</strong> {email_recipients if email_recipients else "(none)"}</div>
            <div><strong>BCC:</strong> {', '.join(bcc_recipients)}</div>
            <div><strong>From:</strong> {sender_email}</div>
            <div><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        </div>

        <div class="email-subject">{subject}</div>

        <div class="email-body">{body}</div>
    </div>
</body>
</html>"""

    html_file = preview_dir / f"{base_filename}.html"
    html_file.write_text(html_content, encoding="utf-8")

    return html_file
