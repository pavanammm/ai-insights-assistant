from sqlalchemy import (
    Column, Integer, String, DateTime, Text,
    ForeignKey, UniqueConstraint
)
from datetime import datetime
from app.db.base import Base
from app.utils.uuid import generate_uuid


class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True)
    response_uuid = Column(String(36), unique=True, default=generate_uuid, nullable=False)

    ticket = Column(String(20), nullable=False)
    revision = Column(String(5), nullable=False)

    member_uuid = Column(String(36), ForeignKey("members.member_uuid"), nullable=False)

    code = Column(String(10), ForeignKey("response_codes.code"))
    facility_type = Column(String(100))
    comments = Column(Text)

    responded_at = Column(DateTime)
    responded_by = Column(String(255))
    ip = Column(String(45))

    attachment_uuid = Column(String(36))
    url = Column(Text)
    webhooked_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)

    __table_args__ = (
        UniqueConstraint("ticket", "revision", "member_uuid", name="uq_response_ticket_member"),
    )
