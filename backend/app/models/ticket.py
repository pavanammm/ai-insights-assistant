from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    Text, Numeric, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
from app.utils.uuid import generate_uuid


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_uuid = Column(String(36), unique=True, default=generate_uuid, nullable=False)

    ticket = Column(String(20), nullable=False)
    revision = Column(String(5), nullable=False, default="000")
    type = Column(String(20), nullable=False)
    priority = Column(String(20))
    category = Column(String(20))

    # Caller
    caller_type = Column(String(50))
    caller_name = Column(String(255))
    caller_phone = Column(String(50))
    caller_email = Column(String(255))
    caller_address = Column(String(255))
    caller_city = Column(String(100))
    caller_state = Column(String(10))
    caller_zip = Column(String(20))

    # Excavator
    excavator_name = Column(String(255))
    excavator_phone = Column(String(50))
    contact_name = Column(String(255))
    contact_phone = Column(String(50))
    done_for = Column(String(255))

    # Location
    state = Column(String(10))
    county = Column(String(100))
    place = Column(String(100))
    street = Column(String(255))
    cross_street1 = Column(String(255))
    cross_street2 = Column(String(255))
    location = Column(Text)
    work_area_geom = Column(Text)

    # Work Info
    work_type = Column(String(255))
    business_hours = Column(Numeric)
    clock_hours = Column(Numeric)
    response_required = Column(Boolean, default=True)

    # Lifecycle Dates
    legal_at = Column(DateTime)
    work_at = Column(DateTime)
    dig_by_at = Column(DateTime)
    response_due_at = Column(DateTime)
    replace_by_at = Column(DateTime)
    expires_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
    created_by = Column(String(100))
    updated_by = Column(String(100))

    __table_args__ = (
        UniqueConstraint("ticket", "revision", name="uq_ticket_revision"),
    )
    dispatches = relationship("Dispatch", backref="ticket_obj")
