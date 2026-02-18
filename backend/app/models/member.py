from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
from app.utils.uuid import generate_uuid


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    member_uuid = Column(String(36), unique=True, default=generate_uuid, nullable=False)

    organization_uuid = Column(String(36), ForeignKey("organizations.organization_uuid"))

    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)

    organization = relationship("Organization", back_populates="members")
