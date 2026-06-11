"""Common typed error payload models for provider responses."""

from __future__ import annotations

from pydantic import Field

from .base import ApiSchema


class ApiErrorDetail(ApiSchema):
    """One error item reported by an external API."""

    code: str | None = None
    message: str
    field: str | None = None


class ApiErrorResponse(ApiSchema):
    """Normalized shape for API error responses."""

    errors: list[ApiErrorDetail] = Field(default_factory=list)
