from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..schemas.llm import AssistantChatRequest, StrategyReviewRequest
from ..services import strategy_service
from ..services.ai_strategy_assistant import AIStrategyAssistant
from ..storage.database import get_db
from ..storage.models import BacktestModel

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/strategy-review")
def strategy_review(req: StrategyReviewRequest, db: Session = Depends(get_db)):
    strategy = strategy_service.get_strategy(db, req.strategy_id)
    if strategy is None:
        raise HTTPException(status_code=404, detail="strategy not found")
    backtest_result = None
    if req.backtest_id:
        model = db.get(BacktestModel, req.backtest_id)
        if model is None:
            raise HTTPException(status_code=404, detail="backtest not found")
        backtest_result = model.result
    result = AIStrategyAssistant().review_strategy(
        strategy.model_dump(),
        backtest_result=backtest_result,
        language=req.language,
        question=req.question,
    )
    return {
        "review": result.text,
        "is_mock": result.is_mock,
        "provider": result.provider,
        "model": result.model,
        "disclaimer": "AI output may be wrong. Not financial advice.",
    }


@router.post("/assistant-chat")
def assistant_chat(req: AssistantChatRequest, db: Session = Depends(get_db)):
    strategy = None
    if req.strategy_id:
        s = strategy_service.get_strategy(db, req.strategy_id)
        if s is not None:
            strategy = s.model_dump()
    result = AIStrategyAssistant().chat(
        message=req.message,
        strategy=strategy,
        history=req.history,
        language=req.language,
    )
    return {
        "reply": result.text,
        "is_mock": result.is_mock,
        "provider": result.provider,
        "model": result.model,
    }
