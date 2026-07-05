from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..schemas.strategy import StrategyCreate, StrategyOut, StrategyUpdate
from ..services import strategy_service
from ..storage.database import get_db

router = APIRouter(prefix="/api/strategies", tags=["strategies"])


@router.post("", response_model=StrategyOut, status_code=201)
def create_strategy(payload: StrategyCreate, db: Session = Depends(get_db)):
    return strategy_service.create_strategy(db, payload)


@router.get("", response_model=list[StrategyOut])
def list_strategies(db: Session = Depends(get_db)):
    return strategy_service.list_strategies(db)


@router.get("/{strategy_id}", response_model=StrategyOut)
def get_strategy(strategy_id: str, db: Session = Depends(get_db)):
    strategy = strategy_service.get_strategy(db, strategy_id)
    if strategy is None:
        raise HTTPException(status_code=404, detail="strategy not found")
    return strategy


@router.put("/{strategy_id}", response_model=StrategyOut)
def update_strategy(strategy_id: str, payload: StrategyUpdate, db: Session = Depends(get_db)):
    strategy = strategy_service.update_strategy(db, strategy_id, payload)
    if strategy is None:
        raise HTTPException(status_code=404, detail="strategy not found")
    return strategy


@router.delete("/{strategy_id}", status_code=204)
def delete_strategy(strategy_id: str, db: Session = Depends(get_db)):
    if not strategy_service.delete_strategy(db, strategy_id):
        raise HTTPException(status_code=404, detail="strategy not found")
