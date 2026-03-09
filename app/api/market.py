from fastapi import APIRouter
from app.core.market_mock import get_mock_market_snapshot

router = APIRouter()

@router.get("/market-snapshot")
def market_snapshot():
    return get_mock_market_snapshot()
