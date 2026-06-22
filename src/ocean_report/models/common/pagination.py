"""Common pagination schemas shared by providers."""

from __future__ import annotations

from pydantic import Field

from .base import ApiSchema


class Pagination(ApiSchema):
    """Standard page-based pagination metadata."""

    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total_items: int = Field(ge=0)


class CursorPagination(ApiSchema):
    """Cursor-based pagination metadata for tokenized APIs."""

    next_cursor: str | None = None
    previous_cursor: str | None = None
