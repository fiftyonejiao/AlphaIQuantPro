from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..schemas.paper_run import PaperRunConfig, PaperRunState
from ..services import strategy_service
from ..services.paper_trading_engine import paper_run_manager
from ..services.run_analysis_service import generate_post_run_analysis
from ..storage.database import get_db
from ..storage.models import PaperRunModel

router = APIRouter(prefix="/api/paper-runs", tags=["paper-runs"])


def _persist(db: Session, state: PaperRunState) -> None:
    model = db.get(PaperRunModel, state.run_id)
    if model is None:
        model = PaperRunModel(
            run_id=state.run_id,
            strategy_id=state.strategy_id,
            status=state.status,
            mode=state.mode,
            state=state.model_dump(),
        )
        db.add(model)
    else:
        model.status = state.status
        model.state = state.model_dump()
    db.commit()


def _get_state(db: Session, run_id: str) -> Optional[PaperRunState]:
    run = paper_run_manager.get(run_id)
    if run is not None:
        return run.snapshot()
    model = db.get(PaperRunModel, run_id)
    if model is not None:
        return PaperRunState(**model.state)
    return None


@router.post("", response_model=PaperRunState, status_code=201)
def start_paper_run(config: PaperRunConfig, db: Session = Depends(get_db)):
    strategy = strategy_service.get_strategy(db, config.strategy_id)
    if strategy is None:
        raise HTTPException(status_code=404, detail="strategy not found")
    if config.mode == "exchange_paper_future":
        raise HTTPException(
            status_code=400,
            detail="exchange_paper_future is disabled — future work, not available in MVP",
        )
    state = paper_run_manager.start_run(config, strategy.model_dump())
    _persist(db, state)
    return state


@router.get("", response_model=list[PaperRunState])
def list_paper_runs(db: Session = Depends(get_db)):
    live = {s.run_id: s for s in paper_run_manager.all_states()}
    for state in live.values():
        _persist(db, state)
    models = db.query(PaperRunModel).order_by(PaperRunModel.created_at.desc()).all()
    out: list[PaperRunState] = []
    for m in models:
        out.append(live.get(m.run_id) or PaperRunState(**m.state))
    return out


@router.get("/{run_id}", response_model=PaperRunState)
def get_paper_run(run_id: str, db: Session = Depends(get_db)):
    state = _get_state(db, run_id)
    if state is None:
        raise HTTPException(status_code=404, detail="paper run not found")
    if paper_run_manager.get(run_id) is not None:
        _persist(db, state)
    return state


@router.post("/{run_id}/stop", response_model=PaperRunState)
def stop_paper_run(run_id: str, db: Session = Depends(get_db)):
    state = paper_run_manager.stop_run(run_id)
    if state is None:
        raise HTTPException(status_code=404, detail="paper run not active")
    _persist(db, state)
    return state


@router.get("/{run_id}/events")
def get_paper_run_events(run_id: str, db: Session = Depends(get_db)):
    state = _get_state(db, run_id)
    if state is None:
        raise HTTPException(status_code=404, detail="paper run not found")
    return {"logs": state.logs, "signals": [s.model_dump() for s in state.signals]}


@router.get("/{run_id}/trades")
def get_paper_run_trades(run_id: str, db: Session = Depends(get_db)):
    state = _get_state(db, run_id)
    if state is None:
        raise HTTPException(status_code=404, detail="paper run not found")
    return {
        "trades": [t.model_dump() for t in state.trades],
        "orders": [o.model_dump() for o in state.orders],
        "fills": [f.model_dump() for f in state.fills],
    }


@router.get("/{run_id}/analysis")
def get_paper_run_analysis(
    run_id: str,
    language: str = Query(default="en"),
    db: Session = Depends(get_db),
):
    state = _get_state(db, run_id)
    if state is None:
        raise HTTPException(status_code=404, detail="paper run not found")
    if state.status == "running":
        raise HTTPException(status_code=409, detail="stop the run before requesting analysis")
    analysis = generate_post_run_analysis(state.model_dump(), language=language)
    state.post_run_analysis = analysis["ai_analysis"]
    _persist(db, state)
    return analysis
