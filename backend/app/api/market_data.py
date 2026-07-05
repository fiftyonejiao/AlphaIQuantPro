from fastapi import APIRouter, HTTPException

from ..schemas.market_data import FetchRequest, MarketDataset, MarketDataStatus
from ..services.data_normalization_service import DataValidationError
from ..services.market_data_service import MarketDataService
from ..services.qveris_client import QverisClient

router = APIRouter(prefix="/api/market-data", tags=["market-data"])


@router.get("/sources")
def get_sources():
    return {"sources": MarketDataService().get_sources()}


@router.get("/status", response_model=MarketDataStatus)
def get_status():
    return MarketDataService().get_status()


@router.post("/fetch", response_model=MarketDataset)
def fetch(req: FetchRequest):
    try:
        return MarketDataService().get_ohlcv(
            req.symbol, req.timeframe, req.start_date, req.end_date, req.market
        )
    except DataValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/qveris/status")
def qveris_status():
    # Never returns the API key — only configuration/reachability state.
    return QverisClient().status().model_dump()


@router.post("/qveris/fetch", response_model=MarketDataset)
def qveris_fetch(req: FetchRequest):
    try:
        return MarketDataService().get_ohlcv(
            req.symbol, req.timeframe, req.start_date, req.end_date, req.market
        )
    except DataValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/qveris/sources")
def qveris_sources():
    client = QverisClient()
    if not client.is_configured:
        return {"configured": False, "capabilities": [], "message": "QVERIS_API_KEY missing — mock fallback active"}
    try:
        from ..services.market_data_service import OHLCV_QUERY

        discovery = client.discover(OHLCV_QUERY, limit=10)
        return {
            "configured": True,
            "search_id": discovery.search_id,
            "capabilities": [c.model_dump() for c in discovery.capabilities],
        }
    except Exception as exc:  # noqa: BLE001
        return {"configured": True, "capabilities": [], "message": f"discover failed: {type(exc).__name__}"}
