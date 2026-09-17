from __future__ import annotations

from typing import Any, Optional

import httpx

from .exceptions import BoxillaAPIError, BoxillaConnectionError

DEFAULT_TIMEOUT = 30.0


def _build_client_kwargs(
    base_url: str,
    username: str,
    password: str,
    verify: bool,
    timeout: float,
    headers: Optional[dict[str, str]],
) -> dict[str, Any]:
    return {
        "base_url": base_url.rstrip("/"),
        "auth": (username, password),
        "verify": verify,
        "timeout": timeout,
        "headers": {"Accept": "application/json", **(headers or {})},
    }


def _raise_for_status(response: httpx.Response) -> None:
    if response.is_error:
        raise BoxillaAPIError.from_response(response)


class BoxillaClient:
    """Synchronous REST API driver for Boxilla, using HTTP Basic auth."""

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        *,
        verify: bool = True,
        timeout: float = DEFAULT_TIMEOUT,
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        self._client = httpx.Client(
            **_build_client_kwargs(base_url, username, password, verify, timeout, headers)
        )

    def request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        try:
            response = self._client.request(method, path, **kwargs)
        except httpx.RequestError as exc:
            raise BoxillaConnectionError(
                f"Could not reach Boxilla at {exc.request.url}: {exc}", original=exc
            ) from exc
        _raise_for_status(response)
        return response

    def get(self, path: str, **kwargs: Any) -> Any:
        return self.request("GET", path, **kwargs).json()

    def post(self, path: str, **kwargs: Any) -> Any:
        return self.request("POST", path, **kwargs).json()

    def put(self, path: str, **kwargs: Any) -> Any:
        return self.request("PUT", path, **kwargs).json()

    def patch(self, path: str, **kwargs: Any) -> Any:
        return self.request("PATCH", path, **kwargs).json()

    def delete(self, path: str, **kwargs: Any) -> Any:
        response = self.request("DELETE", path, **kwargs)
        return response.json() if response.content else None

    def list_kvm_connections(self, **params: Any) -> Any:
        return self.get("/bxa-api/connections/kvm", params=params or None)

    def activate_kvm_connection(self, payload: Optional[dict[str, Any]] = None) -> Any:
        return self.post("/bxa-api/connections/kvm/active", json=payload)

    def list_connection_presets(self, **params: Any) -> Any:
        return self.get("/bxa-api/connections/presets", params=params or None)

    def activate_connection_preset(self, payload: Optional[dict[str, Any]] = None) -> Any:
        return self.post("/bxa-api/connections/presets/activate", json=payload)

    def list_kvm_devices(self, **params: Any) -> Any:
        return self.get("/bxa-api/devices/kvm", params=params or None)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "BoxillaClient":
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.close()


class AsyncBoxillaClient:
    """Asynchronous REST API driver for Boxilla, using HTTP Basic auth."""

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        *,
        verify: bool = True,
        timeout: float = DEFAULT_TIMEOUT,
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        self._client = httpx.AsyncClient(
            **_build_client_kwargs(base_url, username, password, verify, timeout, headers)
        )

    async def request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        try:
            response = await self._client.request(method, path, **kwargs)
        except httpx.RequestError as exc:
            raise BoxillaConnectionError(
                f"Could not reach Boxilla at {exc.request.url}: {exc}", original=exc
            ) from exc
        _raise_for_status(response)
        return response

    async def get(self, path: str, **kwargs: Any) -> Any:
        return (await self.request("GET", path, **kwargs)).json()

    async def post(self, path: str, **kwargs: Any) -> Any:
        return (await self.request("POST", path, **kwargs)).json()

    async def put(self, path: str, **kwargs: Any) -> Any:
        return (await self.request("PUT", path, **kwargs)).json()

    async def patch(self, path: str, **kwargs: Any) -> Any:
        return (await self.request("PATCH", path, **kwargs)).json()

    async def delete(self, path: str, **kwargs: Any) -> Any:
        response = await self.request("DELETE", path, **kwargs)
        return response.json() if response.content else None

    async def list_kvm_connections(self, **params: Any) -> Any:
        return await self.get("/bxa-api/connections/kvm", params=params or None)

    async def activate_kvm_connection(self, payload: Optional[dict[str, Any]] = None) -> Any:
        return await self.post("/bxa-api/connections/kvm/active", json=payload)

    async def list_connection_presets(self, **params: Any) -> Any:
        return await self.get("/bxa-api/connections/presets", params=params or None)

    async def activate_connection_preset(self, payload: Optional[dict[str, Any]] = None) -> Any:
        return await self.post("/bxa-api/connections/presets/activate", json=payload)

    async def list_kvm_devices(self, **params: Any) -> Any:
        return await self.get("/bxa-api/devices/kvm", params=params or None)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncBoxillaClient":
        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        await self.aclose()
