"""Email operations for ocean report workflows."""
from .preview import write_email_preview
from .recipients import get_bcc_recipients
from .sender import send_or_preview_email
from .validator import validate_email_credentials

__all__ = [
    "write_email_preview",
    "get_bcc_recipients",
    "send_or_preview_email",
    "validate_email_credentials",
]
