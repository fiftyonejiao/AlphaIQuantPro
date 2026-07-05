"""Schemas for the QVeris.ai capability-routing gateway.

Real QVeris REST contract (Discover -> Inspect -> Call):
- Discover: POST /search       -> { search_id, results: [ {tool_id, name, params, ...} ] }
- Inspect:  POST /tools/by-ids  -> { results: [ {tool_id, params, examples, ...} ] }
- Call:     POST /tools/execute?tool_id=... -> { execution_id, result: {data}, success, cost }
"""
from typing import Any, Optional

from pydantic import BaseModel, Field


class QverisCapability(BaseModel):
    tool_id: str
    name: str = ""
    description: str = ""
    provider: str = "qveris"
    params: list[str] = Field(default_factory=list)
    expected_cost: Optional[str] = None


class QverisDiscoverResult(BaseModel):
    search_id: Optional[str] = None
    capabilities: list[QverisCapability] = Field(default_factory=list)


class QverisCallResult(BaseModel):
    tool_id: str
    ok: bool
    data: Any = None
    error: Optional[str] = None
    execution_id: Optional[str] = None
    cost: Optional[float] = None
    latency_ms: Optional[float] = None


class QverisStatus(BaseModel):
    configured: bool
    base_url: str
    session_id: str
    reachable: bool = False
    message: str = ""
