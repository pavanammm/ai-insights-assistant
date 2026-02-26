from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
from app.utils.uuid import generate_uuid


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    organization_uuid = Column(String(36), unique=True, default=generate_uuid, nullable=False)

    name = Column(String(255), nullable=False)
    moniker = Column(String(100))
    description = Column(Text)
    ein = Column(String(50))

    address = Column(String(255))
    city = Column(String(100))
    state = Column(String(10))
    zip = Column(String(20))
    country_code = Column(String(10), default="USA")

    email = Column(String(255))
    phone = Column(String(50))
    enable_mfa = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100))
    updated_at = Column(DateTime)
    updated_by = Column(String(100))

    members = relationship("Member", back_populates="organization")
    persons = relationship("Person", back_populates="organization")
