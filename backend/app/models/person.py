from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
from app.utils.uuid import generate_uuid


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True)
    person_uuid = Column(String(36), unique=True, default=generate_uuid, nullable=False)

    organization_uuid = Column(String(36), ForeignKey("organizations.organization_uuid"))

    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255), unique=True)
    phone = Column(String(50))
    role = Column(String(100))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)

    organization = relationship("Organization", back_populates="persons")
