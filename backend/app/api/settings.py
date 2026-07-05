from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..services.deepseek_client import DeepSeekClient
from ..services.qveris_client import QverisClient
from ..storage.database import get_db
from ..storage.models import AppSettingModel

router = APIRouter(prefix="/api/settings", tags=["settings"])

_DEFAULTS: dict[str, Any] = {
    "default_symbol": "AAPL",
    "default_timeframe": "1d",
    "default_initial_capital": 100000,
    "default_fee_rate": 0.001,
    "default_slippage": 0.0005,
    "language": "en",
    "live_trading_enabled": False,  # permanently False in MVP
}


class SettingsUpdate(BaseModel):
    values: dict[str, Any] = Field(default_factory=dict)


@router.get("")
def get_settings_endpoint(db: Session = Depends(get_db)):
    row = db.get(AppSettingModel, "app")
    stored = dict(row.value) if row else {}
    values = {**_DEFAULTS, **stored}
    values["live_trading_enabled"] = False  # hard gate — no live trading in MVP
    deepseek = DeepSeekClient().status()
    qveris = QverisClient().status()
    return {
        "values": values,
        # Status only — API keys are never included in any response.
        "deepseek": deepseek.model_dump(),
        "qveris": {
            "configured": qveris.configured,
            "reachable": qveris.reachable,
            "session_id": qveris.session_id,
            "message": qveris.message,
        },
    }


@router.put("")
def update_settings_endpoint(payload: SettingsUpdate, db: Session = Depends(get_db)):
    row = db.get(AppSettingModel, "app")
    stored = dict(row.value) if row else {}
    incoming = dict(payload.values)
    incoming.pop("live_trading_enabled", None)  # cannot be enabled through the API
    stored.update(incoming)
    if row is None:
        row = AppSettingModel(key="app", value=stored)
        db.add(row)
    else:
        row.value = stored
    db.commit()
    values = {**_DEFAULTS, **stored}
    values["live_trading_enabled"] = False
    return {"values": values}
