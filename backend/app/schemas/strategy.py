from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

StrategyType = Literal["indicator", "script"]


class StrategyBase(BaseModel):
    name: str
    description: str = ""
    strategy_type: StrategyType = "indicator"
    code: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class StrategyCreate(StrategyBase):
    pass


class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    strategy_type: Optional[StrategyType] = None
    code: Optional[str] = None
    parameters: Optional[dict[str, Any]] = None


class StrategyOut(StrategyBase):
    strategy_id: str
    created_at: str
    updated_at: str
