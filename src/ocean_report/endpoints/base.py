"""Shared endpoint abstractions for external API integrations."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TypeVar

from pydantic import BaseModel

from ..api_client.client import ApiClient

TModel = TypeVar("TModel", bound=BaseModel)


class BaseEndpoint:
    """Reusable base class for typed API endpoints.

    Endpoint implementations should focus on API-specific paths and schemas,
    while all HTTP transport behavior remains in ``ApiClient``.
    """

    BASE_URL: str = ""

    def __init__(self, client: ApiClient, *, base_url: str | None = None) -> None:
        self.client = client
        self.base_url = (base_url or self.BASE_URL).strip()

        if not self.base_url:
            raise ValueError("Base URL must be provided via BASE_URL or base_url")

    def build_url(self, path: str = "") -> str:
        """Build an absolute URL from this endpoint's base URL and a path."""

        if not path:
            return self.base_url.rstrip("/")
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    @staticmethod
    def serialize_params(
        params: BaseModel | Mapping[str, object] | None,
    ) -> Mapping[str, object] | None:
        """Convert request params into query-ready mappings."""

        if params is None:
            return None
        if isinstance(params, BaseModel):
            return params.model_dump(by_alias=True, exclude_none=True)
        return params

    def get_response(
        self,
        path: str,
        *,
        params: BaseModel | Mapping[str, object] | None = None,
        headers: Mapping[str, str] | None = None,
    ):
        """Execute a GET request against this endpoint base URL."""

        return self.client.get(
            self.build_url(path),
            params=self.serialize_params(params),
            headers=headers,
        )

    def get_json(
        self,
        path: str,
        *,
        params: BaseModel | Mapping[str, object] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> object:
        """Execute a GET request and return validated JSON payload."""

        return self.client.get_json(
            self.build_url(path),
            params=self.serialize_params(params),
            headers=headers,
        )

    @staticmethod
    def parse_model(model_type: type[TModel], payload: object) -> TModel:
        """Validate and parse a JSON payload into a typed model."""

        return model_type.model_validate(payload)
