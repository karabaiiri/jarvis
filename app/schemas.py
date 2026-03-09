from pydantic import BaseModel

class TradeJournalCreate(BaseModel):
    date: str
    instrument: str
    trade_direction: str
    traded_scenario: str
    entry_price: float
    stop_price: float
    exit_price: float
    points_result: float
    followed_plan: bool
    main_mistake: str
    lesson: str

class TradeJournalResponse(TradeJournalCreate):
    id: int

    class Config:
        from_attributes = True
