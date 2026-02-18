from sqlalchemy import (
    Column, Integer, String, DateTime, Text,
    ForeignKey
)
from datetime import datetime
from app.db.base import Base
from app.utils.uuid import generate_uuid
from sqlalchemy.orm import relationship
from sqlalchemy import Index



class Dispatch(Base):
    __tablename__ = "dispatches"

    id = Column(Integer, primary_key=True, index=True)
    dispatch_uuid = Column(String(36), unique=True, default=generate_uuid, nullable=False)

    ticket_uuid = Column(String(36), ForeignKey("tickets.ticket_uuid"), nullable=False)
    member_uuid = Column(String(36), ForeignKey("members.member_uuid"), nullable=False)

    category = Column(String(50))

    content_text = Column(Text)
    subject = Column(Text)

    destination_to = Column(String(255))
    destination_format = Column(String(50))
    destination_protocol = Column(String(50))

    dispatched_at = Column(DateTime)
    processed_at = Column(DateTime)
    resolved_at = Column(DateTime)

    resolution = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100))
    member = relationship("Member")

Index("idx_dispatch_ticket", Dispatch.ticket_uuid)
Index("idx_dispatch_member", Dispatch.member_uuid)
