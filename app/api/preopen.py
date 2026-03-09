from fastapi import APIRouter
from app.core.preopen_mock import get_mock_preopen_report

router = APIRouter()

@router.get("/preopen-report")
def preopen_report():
    return get_mock_preopen_report()
