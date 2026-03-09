from sqlalchemy import Column, Integer, String, Float, Boolean
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
