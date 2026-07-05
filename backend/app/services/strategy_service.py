"""Strategy CRUD service."""
from typing import Optional

from sqlalchemy.orm import Session

from ..schemas.strategy import StrategyCreate, StrategyOut, StrategyUpdate
from ..storage.models import StrategyModel, utcnow_iso


def _to_out(model: StrategyModel) -> StrategyOut:
    return StrategyOut(
        strategy_id=model.strategy_id,
        name=model.name,
        description=model.description,
        strategy_type=model.strategy_type,  # type: ignore[arg-type]
        code=model.code,
        parameters=model.parameters or {},
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def create_strategy(db: Session, payload: StrategyCreate) -> StrategyOut:
    model = StrategyModel(
        name=payload.name,
        description=payload.description,
        strategy_type=payload.strategy_type,
        code=payload.code,
        parameters=payload.parameters,
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return _to_out(model)


def list_strategies(db: Session) -> list[StrategyOut]:
    models = db.query(StrategyModel).order_by(StrategyModel.created_at.desc()).all()
    return [_to_out(m) for m in models]


def get_strategy(db: Session, strategy_id: str) -> Optional[StrategyOut]:
    model = db.get(StrategyModel, strategy_id)
    return _to_out(model) if model else None


def update_strategy(db: Session, strategy_id: str, payload: StrategyUpdate) -> Optional[StrategyOut]:
    model = db.get(StrategyModel, strategy_id)
    if model is None:
        return None
    data = payload.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in data.items():
        setattr(model, key, value)
    model.updated_at = utcnow_iso()
    db.commit()
    db.refresh(model)
    return _to_out(model)


def delete_strategy(db: Session, strategy_id: str) -> bool:
    model = db.get(StrategyModel, strategy_id)
    if model is None:
        return False
    db.delete(model)
    db.commit()
    return True
