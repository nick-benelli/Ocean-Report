"""Sample tests for email sender.

These tests demonstrate the pattern for testing the emailer module.
"""

from unittest.mock import Mock, patch, MagicMock
import pytest

from ocean_report.emailer.sender import EmailRecipients, send_email


def test_email_recipients_creation():
    """Test EmailRecipients dataclass creation."""
    recipients = EmailRecipients(
        to_email="test@example.com", bcc_list=["user1@example.com", "user2@example.com"]
    )

    assert recipients.to_email == "test@example.com"
    assert len(recipients.bcc_list) == 2
    assert "user1@example.com" in recipients.bcc_list


def test_email_recipients_immutable():
    """Test that EmailRecipients is immutable (frozen)."""
    recipients = EmailRecipients(to_email="test@example.com")

    with pytest.raises(Exception):  # FrozenInstanceError
        recipients.to_email = "new@example.com"


def test_send_email_requires_password():
    """Test that send_email requires a password."""
    with pytest.raises(ValueError, match="Email password must be provided"):
        send_email(
            subject="Test",
            body="Test body",
            sender_email="test@example.com",
            email_password=None,
            smtp_server="smtp.example.com",
            smtp_port=587,
        )


def test_send_email_with_valid_params():
    """Test send_email with valid parameters (mocked SMTP)."""
    recipients = EmailRecipients(
        to_email="recipient@example.com", bcc_list=["bcc1@example.com"]
    )

    with patch("smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        send_email(
            subject="Test Subject",
            body="Test Body",
            sender_email="sender@example.com",
            email_password="test_password",
            recipients=recipients,
            smtp_server="smtp.example.com",
            smtp_port=587,
        )

        # Verify SMTP was called
        mock_smtp.assert_called_once_with("smtp.example.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("sender@example.com", "test_password")
