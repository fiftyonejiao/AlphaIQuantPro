from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..schemas.backtest import BacktestConfig, BacktestResult, BacktestSummary
from ..services import strategy_service
from ..services.backtest_engine import run_backtest
from ..services.data_normalization_service import DataValidationError
from ..services.market_data_service import MarketDataService
from ..services.strategy_sandbox import StrategySandboxError
from ..storage.database import get_db
from ..storage.models import BacktestModel, StrategyModel

router = APIRouter(prefix="/api/backtests", tags=["backtests"])


@router.post("", response_model=BacktestResult, status_code=201)
def create_backtest(config: BacktestConfig, db: Session = Depends(get_db)):
    strategy = strategy_service.get_strategy(db, config.strategy_id)
    if strategy is None:
        raise HTTPException(status_code=404, detail="strategy not found")

    service = MarketDataService()
    try:
        dataset = service.get_ohlcv(
            config.symbol, config.timeframe, config.start_date, config.end_date
        )
        result = run_backtest(strategy.model_dump(), config, dataset)
    except DataValidationError as exc:
        raise HTTPException(status_code=422, detail=f"market data invalid: {exc}") from exc
    except StrategySandboxError as exc:
        raise HTTPException(status_code=422, detail=f"strategy error: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    model = BacktestModel(
        backtest_id=result.backtest_id,
        strategy_id=result.strategy_id,
        symbol=result.symbol,
        timeframe=result.timeframe,
        start_date=result.start_date,
        end_date=result.end_date,
        initial_capital=result.initial_capital,
        final_equity=result.final_equity,
        status=result.status,
        result=result.model_dump(),
    )
    db.add(model)
    db.commit()
    result.created_at = model.created_at
    return result


def _load(db: Session, backtest_id: str) -> BacktestModel:
    model = db.get(BacktestModel, backtest_id)
    if model is None:
        raise HTTPException(status_code=404, detail="backtest not found")
    return model


@router.get("", response_model=list[BacktestSummary])
def list_backtests(db: Session = Depends(get_db)):
    models = db.query(BacktestModel).order_by(BacktestModel.created_at.desc()).all()
    names = {s.strategy_id: s.name for s in db.query(StrategyModel).all()}
    summaries = []
    for m in models:
        metrics = (m.result or {}).get("metrics", {})
        summaries.append(
            BacktestSummary(
                backtest_id=m.backtest_id,
                strategy_id=m.strategy_id,
                strategy_name=names.get(m.strategy_id, ""),
                symbol=m.symbol,
                timeframe=m.timeframe,
                start_date=m.start_date,
                end_date=m.end_date,
                status=m.status,
                total_return=metrics.get("total_return", 0.0),
                max_drawdown=metrics.get("max_drawdown", 0.0),
                trade_count=metrics.get("trade_count", 0),
                is_mock_data=(m.result or {}).get("is_mock_data", True),
                created_at=m.created_at,
            )
        )
    return summaries


@router.get("/{backtest_id}")
def get_backtest(backtest_id: str, db: Session = Depends(get_db)):
    model = _load(db, backtest_id)
    result = dict(model.result or {})
    result["created_at"] = model.created_at
    return result


@router.get("/{backtest_id}/events")
def get_backtest_events(backtest_id: str, db: Session = Depends(get_db)):
    model = _load(db, backtest_id)
    return {"logs": (model.result or {}).get("logs", [])}


@router.get("/{backtest_id}/trades")
def get_backtest_trades(backtest_id: str, db: Session = Depends(get_db)):
    model = _load(db, backtest_id)
    return {"trades": (model.result or {}).get("trades", [])}


@router.get("/{backtest_id}/metrics")
def get_backtest_metrics(backtest_id: str, db: Session = Depends(get_db)):
    model = _load(db, backtest_id)
    return {"metrics": (model.result or {}).get("metrics", {})}
