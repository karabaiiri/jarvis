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


class MarketOutcomeCreate(BaseModel):
    date: str
    instrument: str
    actual_day_direction: str
    actual_primary_move: str
    best_scenario_match: str
    did_market_follow_primary_scenario: bool
    range_expansion_happened: bool
    points_from_open_to_main_move: float
    market_notes: str

class MarketOutcomeResponse(MarketOutcomeCreate):
    id: int

    class Config:
        from_attributes = True
