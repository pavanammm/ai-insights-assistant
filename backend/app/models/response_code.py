from sqlalchemy import Column, String, Boolean, Text
from app.db.base import Base


class ResponseCode(Base):
    __tablename__ = "response_codes"

    code = Column(String(10), primary_key=True)
    description = Column(Text, nullable=False)
    active = Column(Boolean, default=True)
