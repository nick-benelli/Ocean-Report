"""Jinja2 template rendering for email generation."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, TemplateError

from ..config import get_settings, get_template_path
from ..logger import logger
from ..models.email import EmailTemplateData


def render_email_template(
    data: EmailTemplateData,
    template_path: Optional[str | Path] = None,
) -> str:
    """
    Render email body from Jinja2 template.

    Args:
        data: Template data containing all variables
        template_path: Optional custom template path (string or Path).
                      If None, uses path from config.

    Returns:
        Rendered email body as string

    Raises:
        FileNotFoundError: If template file doesn't exist
        jinja2.TemplateError: If template rendering fails
    """
    # Get template path from config if not provided
    if template_path is None:
        template_path = get_template_path()
        logger.info("Using template from config: %s", template_path)
    else:
        # Convert string to Path if necessary
        if isinstance(template_path, str):
            template_path = Path(template_path)
        logger.info("Using custom template: %s", template_path)

    # Validate template exists
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")

    logger.info("Rendering email template: %s", template_path.name)

    try:
        # Set up Jinja2 environment
        env = Environment(
            loader=FileSystemLoader(template_path.parent),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,  # Email is plain text, not HTML
        )

        # Load template
        template = env.get_template(template_path.name)

        # Get config for defaults (used in template filters/fallbacks)
        config = get_settings()

        # Render with data, providing config defaults for fallback values
        rendered = template.render(
            **data.to_template_dict(),
            # These can be used as fallbacks in the template
            default_station_name=config.reporting.station_name,
            default_wind_provider=config.reporting.wind_provider,
        )

        logger.info("Email template rendered successfully")
        return rendered

    except TemplateError as e:
        logger.error("Template rendering failed: %s", e)
        raise


def load_template_content(template_path: Optional[str | Path] = None) -> str:
    """
    Load raw template content without rendering.

    Useful for template validation, debugging, or preview.

    Args:
        template_path: Optional custom template path (string or Path).
                      If None, uses path from config.

    Returns:
        Raw template file content

    Raises:
        FileNotFoundError: If template file doesn't exist
    """
    if template_path is None:
        template_path = get_template_path()
    elif isinstance(template_path, str):
        template_path = Path(template_path)

    logger.debug("Loading template content: %s", template_path)
    return template_path.read_text(encoding="utf-8")


__all__ = ["EmailTemplateData", "render_email_template", "load_template_content"]
