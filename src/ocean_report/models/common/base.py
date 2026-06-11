"""Shared Pydantic model conventions for API schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ApiSchema(BaseModel):
    """Base schema for external API request/response models.

    Conventions:
    - immutable instances for safer use across services
    - reject unknown fields to detect API drift quickly
    - allow field population by alias and field name
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        populate_by_name=True,
    )
