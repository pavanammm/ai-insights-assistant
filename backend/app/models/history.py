from sqlalchemy import (
    Column, Integer, String, DateTime, Text
)
from datetime import datetime
from app.db.base import Base
from sqlalchemy import Index

class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True)

    schemaname = Column(String(100))
    tabname = Column(String(100))
    operation = Column(String(10))

    old_val = Column(Text)
    new_val = Column(Text)

    who = Column(String(255))
    tstamp = Column(DateTime, default=datetime.utcnow)


    
Index("idx_history_tab", History.tabname)
Index("idx_history_time", History.tstamp)
