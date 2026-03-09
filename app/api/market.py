from fastapi import APIRouter, Query
from app.core.market_mock import get_mock_market_snapshot

router = APIRouter()

@router.get("/market-snapshot")
def market_snapshot(regime: str = Query(default="bullish"), date: str = Query(default=None)):
    return get_mock_market_snapshot(regime, date)
