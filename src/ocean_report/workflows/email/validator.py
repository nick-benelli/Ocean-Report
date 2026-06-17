"""Email configuration validation."""


def validate_email_credentials(sender: str | None, password: str | None) -> None:
    """Validate that required email credentials are configured.

    Args:
        sender: Email sender address
        password: Email password

    Raises:
        ValueError: If required credentials are missing
    """
    if not sender:
        raise ValueError(
            "Email sender address is not configured. "
            "Set EMAIL_SENDER environment variable or email.sender in config."
        )
    if not password:
        raise ValueError(
            "Email password is not configured. "
            "Set EMAIL_PASSWORD environment variable or email.password in config."
        )
