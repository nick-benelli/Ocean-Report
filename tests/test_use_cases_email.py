"""Tests for email use cases."""

from datetime import date
from unittest.mock import Mock, patch
import pytest

from ocean_report.application.context import ApplicationContext
from ocean_report.config.schemas import AppConfig, EmailConfig, SummerConfig, RecipientUrlsConfig
from ocean_report.use_cases.email import get_email_recipients


@pytest.fixture
def mock_context_summer():
    """Create a mock context for summer period."""
    config = AppConfig(
        email=EmailConfig(
            smtp_server="smtp.example.com",
            smtp_port=587,
            sender="test@example.com",
            recipient_urls=RecipientUrlsConfig(
                main="https://gist.example.com/main",
                offseason="https://gist.example.com/offseason",
                test="https://gist.example.com/test"
            )
        ),
        summer=SummerConfig(
            memorial_day_offset=-4,
            labor_day_offset=7
        )
    )
    return ApplicationContext(config=config, client=Mock())


@pytest.fixture
def mock_context_offseason():
    """Create a mock context for off-season period."""
    config = AppConfig(
        email=EmailConfig(
            smtp_server="smtp.example.com",
            smtp_port=587,
            sender="test@example.com",
            recipient_urls=RecipientUrlsConfig(
                main="https://gist.example.com/main",
                offseason="https://gist.example.com/offseason",
                test="https://gist.example.com/test"
            )
        ),
        summer=SummerConfig(
            memorial_day_offset=-4,
            labor_day_offset=7
        )
    )
    return ApplicationContext(config=config, client=Mock())


def test_get_email_recipients_uses_main_url_in_summer(mock_context_summer):
    """Test that main recipient URL is used during summer."""
    
    summer_date = date(2025, 7, 4)  # July 4th is definitely summer
    
    with patch("ocean_report.use_cases.email.determine_is_summer") as mock_is_summer, \
         patch("ocean_report.use_cases.email.fetch_recipients_from_gist") as mock_fetch, \
         patch("ocean_report.use_cases.email.parse_recipients") as mock_parse:
        
        mock_is_summer.return_value = True
        mock_fetch.return_value = "user1@example.com\nuser2@example.com"
        mock_parse.return_value = "user1@example.com,user2@example.com"
        
        result = get_email_recipients(context=mock_context_summer, test_recips=False)
        
        # Verify main URL was used
        call_args = mock_fetch.call_args
        assert call_args.kwargs["url"] == "https://gist.example.com/main"
        
        assert result == "user1@example.com,user2@example.com"


def test_get_email_recipients_uses_offseason_url_in_winter(mock_context_offseason):
    """Test that offseason recipient URL is used during winter."""
    
    winter_date = date(2025, 1, 15)  # January is definitely off-season
    
    with patch("ocean_report.use_cases.email.determine_is_summer") as mock_is_summer, \
         patch("ocean_report.use_cases.email.fetch_recipients_from_gist") as mock_fetch, \
         patch("ocean_report.use_cases.email.parse_recipients") as mock_parse:
        
        mock_is_summer.return_value = False
        mock_fetch.return_value = "admin@example.com"
        mock_parse.return_value = "admin@example.com"
        
        result = get_email_recipients(context=mock_context_offseason, test_recips=False)
        
        # Verify offseason URL was used
        call_args = mock_fetch.call_args
        assert call_args.kwargs["url"] == "https://gist.example.com/offseason"
        
        assert result == "admin@example.com"


def test_get_email_recipients_uses_test_url_when_flag_set(mock_context_summer):
    """Test that test recipient URL is used when test_recips=True."""
    
    with patch("ocean_report.use_cases.email.determine_is_summer") as mock_is_summer, \
         patch("ocean_report.use_cases.email.fetch_recipients_from_gist") as mock_fetch, \
         patch("ocean_report.use_cases.email.parse_recipients") as mock_parse:
        
        mock_is_summer.return_value = True  # Even in summer
        mock_fetch.return_value = "test@example.com"
        mock_parse.return_value = "test@example.com"
        
        result = get_email_recipients(context=mock_context_summer, test_recips=True)
        
        # Verify test URL was used (overrides season logic)
        call_args = mock_fetch.call_args
        assert call_args.kwargs["url"] == "https://gist.example.com/test"
        
        assert result == "test@example.com"


def test_get_email_recipients_creates_default_context_when_none(mock_context_summer):
    """Test that default context is created when none provided."""
    
    with patch("ocean_report.use_cases.email.create_application_context") as mock_create, \
         patch("ocean_report.use_cases.email.determine_is_summer") as mock_is_summer, \
         patch("ocean_report.use_cases.email.fetch_recipients_from_gist") as mock_fetch, \
         patch("ocean_report.use_cases.email.parse_recipients") as mock_parse:
        
        mock_create.return_value = mock_context_summer
        mock_is_summer.return_value = True
        mock_fetch.return_value = "user@example.com"
        mock_parse.return_value = "user@example.com"
        
        result = get_email_recipients(context=None, test_recips=False)
        
        # Verify context was created
        mock_create.assert_called_once()
        assert result == "user@example.com"


def test_get_email_recipients_parses_and_cleans_recipients(mock_context_summer):
    """Test that recipient list is parsed and cleaned."""
    
    raw_recipients = "  USER1@EXAMPLE.COM  \n user2@example.com \n\n USER3@EXAMPLE.COM  "
    cleaned_recipients = "user1@example.com,user2@example.com,user3@example.com"
    
    with patch("ocean_report.use_cases.email.determine_is_summer") as mock_is_summer, \
         patch("ocean_report.use_cases.email.fetch_recipients_from_gist") as mock_fetch, \
         patch("ocean_report.use_cases.email.parse_recipients") as mock_parse:
        
        mock_is_summer.return_value = True
        mock_fetch.return_value = raw_recipients
        mock_parse.return_value = cleaned_recipients
        
        result = get_email_recipients(context=mock_context_summer, test_recips=False)
        
        # Verify parsing was called with raw data
        mock_parse.assert_called_once_with(raw_recipients, verbose=False)
        
        # Verify result is cleaned
        assert result == cleaned_recipients
