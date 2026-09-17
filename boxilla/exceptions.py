from __future__ import annotations

import httpx


class BoxillaError(Exception):
    """Base exception for all errors raised by this driver."""


class BoxillaConnectionError(BoxillaError):
    """Raised when the Boxilla server could not be reached at all."""

    def __init__(self, message: str, *, original: Exception | None = None) -> None:
        super().__init__(message)
        self.original = original


class BoxillaAPIError(BoxillaError):
    """Raised when Boxilla returns a non-2xx response."""

    def __init__(self, message: str, *, response: httpx.Response) -> None:
        super().__init__(message)
        self.response = response
        self.status_code = response.status_code

    @classmethod
    def from_response(cls, response: httpx.Response) -> "BoxillaAPIError":
        if response.status_code in (401, 403):
            error_cls: type[BoxillaAPIError] = BoxillaAuthError
        else:
            error_cls = cls

        try:
            payload = response.json()
            detail = payload.get("message") or payload.get("error") or payload
        except ValueError:
            detail = response.text

        message = f"Boxilla API error ({response.status_code}) for {response.request.method} {response.request.url}: {detail}"
        return error_cls(message, response=response)


class BoxillaAuthError(BoxillaAPIError):
    """Raised on authentication/authorization failures (401/403)."""
