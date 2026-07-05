"""Schemas for the QVeris.ai capability-routing gateway."""
from typing import Any, Optional

from pydantic import BaseModel, Field


class QverisCapability(BaseModel):
    capability_id: str
    name: str
    category: str
    description: str = ""
    provider: str = "qveris"


class QverisDiscoverResponse(BaseModel):
    capabilities: list[QverisCapability] = Field(default_factory=list)


class QverisCallRequest(BaseModel):
    capability_id: str
    params: dict[str, Any] = Field(default_factory=dict)


class QverisCallResult(BaseModel):
    capability_id: str
    ok: bool
    data: Any = None
    error: Optional[str] = None
    latency_ms: Optional[float] = None


class QverisStatus(BaseModel):
    configured: bool
    base_url: str
    session_id: str
    reachable: bool = False
    message: str = ""
