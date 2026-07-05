"""QVeris.ai client — the single gateway for financial/market data.

Implements the real QVeris **Discover -> Inspect -> Call** REST workflow:

- Discover: ``POST /search``       (free) -> ranked capabilities + ``search_id``
- Inspect:  ``POST /tools/by-ids`` (free) -> full parameter schemas
- Call:     ``POST /tools/execute?tool_id=...`` (may consume credits) -> ``result.data``

All calls stay behind ``market_data_service``; nothing else in the app talks
to QVeris. The API key is read from environment variables only and never logged.
"""
import time
from typing import Any, Optional

import httpx

from ..config import get_settings
from ..schemas.qveris import (
    QverisCallResult,
    QverisCapability,
    QverisDiscoverResult,
    QverisStatus,
)


class QverisNotConfiguredError(RuntimeError):
    """Raised when QVERIS_API_KEY is missing and a real call is attempted."""


class QverisClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        session_id: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        settings = get_settings()
        self.api_key = api_key if api_key is not None else settings.qveris_api_key
        self.base_url = (base_url or settings.qveris_base_url).rstrip("/")
        self.session_id = session_id or settings.qveris_session_id
        self.timeout = timeout

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key) and self.api_key != "your_qveris_api_key_here"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _require_configured(self) -> None:
        if not self.is_configured:
            raise QverisNotConfiguredError(
                "QVERIS_API_KEY is not configured; use mock fallback instead."
            )

    def status(self) -> QverisStatus:
        status = QverisStatus(
            configured=self.is_configured,
            base_url=self.base_url,
            session_id=self.session_id,
        )
        if not self.is_configured:
            status.message = "QVERIS_API_KEY missing — mock data fallback active"
            return status
        # A free discover call is the cheapest reliable reachability probe.
        try:
            result = self.discover("stock price", limit=1)
            status.reachable = True
            status.message = (
                f"reachable — discovered {len(result.capabilities)} capability(ies)"
            )
        except (httpx.HTTPError, ValueError) as exc:
            status.reachable = False
            status.message = f"unreachable: {type(exc).__name__}"
        return status

    @staticmethod
    def _param_names(raw_params: Any) -> list[str]:
        names: list[str] = []
        if isinstance(raw_params, list):
            for p in raw_params:
                if isinstance(p, dict) and p.get("name"):
                    names.append(str(p["name"]))
                elif isinstance(p, str):
                    names.append(p)
        return names

    def discover(self, query: str, limit: int = 20) -> QverisDiscoverResult:
        """Discover capabilities with a natural-language query (free)."""
        self._require_configured()
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                f"{self.base_url}/search",
                headers=self._headers(),
                json={"query": query, "limit": limit, "session_id": self.session_id},
            )
            resp.raise_for_status()
            payload = resp.json()
        capabilities = [
            QverisCapability(
                tool_id=str(item.get("tool_id") or item.get("capability_id", "")),
                name=str(item.get("name", "")),
                description=str(item.get("description", "")),
                provider=str(item.get("provider_name", item.get("provider", "qveris"))),
                params=self._param_names(item.get("params")),
                expected_cost=item.get("expected_cost"),
            )
            for item in payload.get("results", [])
        ]
        return QverisDiscoverResult(
            search_id=payload.get("search_id"), capabilities=capabilities
        )

    def inspect(
        self, tool_ids: list[str], search_id: Optional[str] = None
    ) -> list[QverisCapability]:
        """Inspect capabilities' full parameter schemas (free)."""
        self._require_configured()
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                f"{self.base_url}/tools/by-ids",
                headers=self._headers(),
                json={
                    "tool_ids": tool_ids,
                    "search_id": search_id,
                    "session_id": self.session_id,
                },
            )
            resp.raise_for_status()
            payload = resp.json()
        return [
            QverisCapability(
                tool_id=str(item.get("tool_id", "")),
                name=str(item.get("name", "")),
                description=str(item.get("description", "")),
                provider=str(item.get("provider_name", item.get("provider", "qveris"))),
                params=self._param_names(item.get("params")),
                expected_cost=item.get("expected_cost"),
            )
            for item in payload.get("results", [])
        ]

    def call(
        self,
        tool_id: str,
        parameters: dict[str, Any],
        search_id: Optional[str] = None,
        max_response_size: int = -1,
    ) -> QverisCallResult:
        """Execute a capability (may consume credits) and return its raw data."""
        self._require_configured()
        started = time.monotonic()
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(
                    f"{self.base_url}/tools/execute",
                    headers=self._headers(),
                    params={"tool_id": tool_id},
                    json={
                        "search_id": search_id,
                        "session_id": self.session_id,
                        "parameters": parameters,
                        "max_response_size": max_response_size,
                    },
                )
                resp.raise_for_status()
                payload = resp.json()
            latency = (time.monotonic() - started) * 1000
            if not payload.get("success", False):
                return QverisCallResult(
                    tool_id=tool_id,
                    ok=False,
                    error=str(payload.get("error_message") or "call failed"),
                    execution_id=payload.get("execution_id"),
                    cost=payload.get("cost"),
                    latency_ms=latency,
                )
            return QverisCallResult(
                tool_id=tool_id,
                ok=True,
                data=(payload.get("result") or {}).get("data"),
                execution_id=payload.get("execution_id"),
                cost=payload.get("cost"),
                latency_ms=latency,
            )
        except httpx.HTTPError as exc:
            return QverisCallResult(
                tool_id=tool_id,
                ok=False,
                error=f"{type(exc).__name__}: {exc}",
                latency_ms=(time.monotonic() - started) * 1000,
            )
