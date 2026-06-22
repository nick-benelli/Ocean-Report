"""Tests for workflow email operations."""

from unittest.mock import Mock, patch, MagicMock
import pytest

from ocean_report.application.context import ApplicationContext
from ocean_report.config.schemas import AppConfig, EmailConfig
from ocean_report.workflows.email import get_bcc_recipients, send_or_preview_email


@pytest.fixture
def mock_context():
    """Create a mock application context."""
    config = AppConfig(
        email=EmailConfig(
            smtp_server="smtp.example.com",
            smtp_port=587,
            sender="sender@example.com",
            password="test_password",
            recipients="recipient@example.com",
        )
    )
    return ApplicationContext(config=config, client=Mock())


# Tests for get_bcc_recipients


def test_get_bcc_recipients_fetches_from_url_when_enabled():
    """Test that recipients are fetched from URL when use_url=True."""
    
    with patch("ocean_report.workflows.email.recipients.get_email_recipients") as mock_get:
        mock_get.return_value = "user1@example.com,user2@example.com,user3@example.com"
        
        result = get_bcc_recipients(
            test=False,
            use_url=True,
            fallback_recipients="fallback@example.com"
        )
        
        assert len(result) == 3
        assert "user1@example.com" in result
        assert "user2@example.com" in result
        assert "user3@example.com" in result
        
        # Verify URL fetch was called
        mock_get.assert_called_once_with(test_recips=False)


def test_get_bcc_recipients_uses_fallback_when_url_disabled():
    """Test that fallback recipients are used when use_url=False."""
    
    with patch("ocean_report.workflows.email.recipients.get_email_recipients") as mock_get:
        result = get_bcc_recipients(
            test=False,
            use_url=False,
            fallback_recipients="admin1@example.com,admin2@example.com"
        )
        
        assert len(result) == 2
        assert "admin1@example.com" in result
        assert "admin2@example.com" in result
        
        # Verify URL fetch was NOT called
        mock_get.assert_not_called()


def test_get_bcc_recipients_uses_test_mode_when_flag_set():
    """Test that test=True is passed to recipient fetcher."""
    
    with patch("ocean_report.workflows.email.recipients.get_email_recipients") as mock_get:
        mock_get.return_value = "test@example.com"
        
        result = get_bcc_recipients(
            test=True,
            use_url=True,
            fallback_recipients=""
        )
        
        assert result == ["test@example.com"]
        mock_get.assert_called_once_with(test_recips=True)


def test_get_bcc_recipients_strips_whitespace():
    """Test that email addresses are stripped of whitespace."""
    
    with patch("ocean_report.workflows.email.recipients.get_email_recipients") as mock_get:
        mock_get.return_value = "  user1@example.com  , user2@example.com ,  user3@example.com  "
        
        result = get_bcc_recipients(
            test=False,
            use_url=True,
            fallback_recipients=""
        )
        
        # All emails should be stripped
        assert result == ["user1@example.com", "user2@example.com", "user3@example.com"]


def test_get_bcc_recipients_filters_empty_strings():
    """Test that empty strings are filtered out."""
    
    with patch("ocean_report.workflows.email.recipients.get_email_recipients") as mock_get:
        mock_get.return_value = "user1@example.com,,,user2@example.com,"
        
        result = get_bcc_recipients(
            test=False,
            use_url=True,
            fallback_recipients=""
        )
        
        # Only valid emails should remain
        assert len(result) == 2
        assert result == ["user1@example.com", "user2@example.com"]


def test_get_bcc_recipients_handles_empty_fallback():
    """Test handling of empty fallback recipients."""
    
    result = get_bcc_recipients(
        test=False,
        use_url=False,
        fallback_recipients=""
    )
    
    assert result == []


# Tests for send_or_preview_email


def test_send_or_preview_email_prints_preview_when_run_email_false(mock_context, capsys):
    """Test that email preview is printed when run_email=False."""
    
    send_or_preview_email(
        context=mock_context,
        run_email=False,
        subject="Test Subject",
        body="Test Body",
        bcc_recipients=["user1@example.com", "user2@example.com"],
    )
    
    # Capture printed output
    captured = capsys.readouterr()
    
    # Verify preview was printed (not sent)
    assert "Test Subject" in captured.out or "Test Body" in captured.out


def test_send_or_preview_email_sends_via_smtp_when_run_email_true(mock_context):
    """Test that email is sent via SMTP when run_email=True."""
    
    with patch("ocean_report.workflows.email.sender.emailer.send_email") as mock_send:
        send_or_preview_email(
            context=mock_context,
            run_email=True,
            subject="Test Subject",
            body="Test Body",
            bcc_recipients=["user1@example.com"],
        )
        
        # Verify send_email was called
        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args.kwargs
        assert call_kwargs["subject"] == "Test Subject"
        assert call_kwargs["body"] == "Test Body"
        assert call_kwargs["sender_email"] == "sender@example.com"
        assert call_kwargs["email_password"] == "test_password"


def test_send_or_preview_email_uses_context_config(mock_context):
    """Test that email config is taken from context."""
    
    with patch("ocean_report.workflows.email.sender.emailer.send_email") as mock_send:
        send_or_preview_email(
            context=mock_context,
            run_email=True,
            subject="Test",
            body="Body",
            bcc_recipients=[],
        )
        
        # Verify config values were used
        call_kwargs = mock_send.call_args.kwargs
        assert call_kwargs["smtp_server"] == "smtp.example.com"
        assert call_kwargs["smtp_port"] == 587
        assert call_kwargs["sender_email"] == "sender@example.com"


def test_send_or_preview_email_passes_bcc_list(mock_context):
    """Test that BCC list is passed correctly."""
    
    bcc_list = ["bcc1@example.com", "bcc2@example.com", "bcc3@example.com"]
    
    with patch("ocean_report.workflows.email.sender.emailer.send_email") as mock_send:
        send_or_preview_email(
            context=mock_context,
            run_email=True,
            subject="Test",
            body="Body",
            bcc_recipients=bcc_list,
        )
        
        # Verify BCC list was passed
        call_kwargs = mock_send.call_args.kwargs
        assert "bcc_list" in call_kwargs or "recipients" in call_kwargs
