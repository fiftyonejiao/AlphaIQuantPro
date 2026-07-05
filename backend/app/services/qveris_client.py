"""QVeris.ai client — the single gateway for financial/market data.

Implements the QVeris discover -> inspect -> call workflow. All calls stay
behind `market_data_service`; nothing else in the app talks to QVeris.
The API key is read from environment variables only and never logged.
"""
import time
from typing import Any, Optional

import httpx

from ..config import get_settings
from ..schemas.qveris import (
    QverisCallResult,
    QverisCapability,
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
        timeout: float = 15.0,
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
            "X-Session-Id": self.session_id,
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
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(f"{self.base_url}/health", headers=self._headers())
                status.reachable = resp.status_code < 500
                status.message = f"health status {resp.status_code}"
        except httpx.HTTPError as exc:
            status.reachable = False
            status.message = f"unreachable: {type(exc).__name__}"
        return status

    def discover(self, category: Optional[str] = None) -> list[QverisCapability]:
        """Discover available data capabilities (quotes, OHLCV, news, ...)."""
        self._require_configured()
        params: dict[str, Any] = {}
        if category:
            params["category"] = category
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(
                f"{self.base_url}/capabilities",
                headers=self._headers(),
                params=params,
            )
            resp.raise_for_status()
            payload = resp.json()
        items = payload.get("capabilities", payload if isinstance(payload, list) else [])
        return [
            QverisCapability(
                capability_id=str(item.get("id") or item.get("capability_id", "")),
                name=str(item.get("name", "")),
                category=str(item.get("category", category or "unknown")),
                description=str(item.get("description", "")),
                provider=str(item.get("provider", "qveris")),
            )
            for item in items
        ]

    def inspect(self, capability_id: str) -> dict[str, Any]:
        """Inspect a capability's schema/params before calling it."""
        self._require_configured()
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(
                f"{self.base_url}/capabilities/{capability_id}",
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()

    def call(self, capability_id: str, params: dict[str, Any]) -> QverisCallResult:
        """Call a capability and return its raw (un-normalized) result."""
        self._require_configured()
        started = time.monotonic()
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(
                    f"{self.base_url}/call",
                    headers=self._headers(),
                    json={"capability_id": capability_id, "params": params},
                )
                resp.raise_for_status()
                data = resp.json()
            return QverisCallResult(
                capability_id=capability_id,
                ok=True,
                data=data,
                latency_ms=(time.monotonic() - started) * 1000,
            )
        except httpx.HTTPError as exc:
            return QverisCallResult(
                capability_id=capability_id,
                ok=False,
                error=f"{type(exc).__name__}: {exc}",
                latency_ms=(time.monotonic() - started) * 1000,
            )
