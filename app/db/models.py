from sqlalchemy import Column, Integer, String, Float, Boolean, Text
from app.db.database import Base

class TradeJournal(Base):
    __tablename__ = "trade_journal"

    id               = Column(Integer, primary_key=True, index=True)
    date             = Column(String)
    instrument       = Column(String)
    trade_direction  = Column(String)
    traded_scenario  = Column(String)
    entry_price      = Column(Float)
    stop_price       = Column(Float)
    exit_price       = Column(Float)
    points_result    = Column(Float)
    followed_plan    = Column(Boolean)
    main_mistake     = Column(String)
    lesson           = Column(String)


class PreopenReport(Base):
    __tablename__ = "preopen_reports"

    id                 = Column(Integer, primary_key=True, index=True)
    created_at         = Column(String)   # ISO datetime string, e.g. "2026-03-07T08:30:00"
    date               = Column(String)   # trading date from the report
    instrument         = Column(String)
    regime             = Column(String)
    primary_bias       = Column(String)
    expansion_potential = Column(String)
    report_json        = Column(Text)     # full report stored as a JSON string


class MarketOutcome(Base):
    __tablename__ = "market_outcomes"

    id                                = Column(Integer, primary_key=True, index=True)
    date                              = Column(String)
    instrument                        = Column(String)
    actual_day_direction              = Column(String)   # e.g. "bullish", "bearish", "neutral"
    actual_primary_move               = Column(String)   # e.g. "broke above ONH", "sold off to PDL"
    best_scenario_match               = Column(String)   # name of the scenario that played out
    did_market_follow_primary_scenario = Column(Boolean)
    range_expansion_happened          = Column(Boolean)
    points_from_open_to_main_move     = Column(Float)
    market_notes                      = Column(String)
