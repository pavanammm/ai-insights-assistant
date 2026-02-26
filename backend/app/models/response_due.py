from sqlalchemy import (
    Column, Integer, String, DateTime,
    ForeignKey
)
from datetime import datetime
from app.db.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Index


class ResponseDue(Base):
    __tablename__ = "responses_due"

    id = Column(Integer, primary_key=True)

    ticket = Column(String(20), nullable=False)
    revision = Column(String(5), nullable=False)

    member_uuid = Column(String(36), ForeignKey("members.member_uuid"), nullable=False)

    due_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    member = relationship("Member")

Index("idx_response_due_ticket", ResponseDue.ticket)
Index("idx_response_due_member", ResponseDue.member_uuid)