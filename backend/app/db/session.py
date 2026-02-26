import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.db.base import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./insights.db")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

# 🔒 Enable SQLite foreign key enforcement
if "sqlite" in DATABASE_URL:
    @event.listens_for(engine, "connect")
    def enable_sqlite_fk(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def init_db():
    from app import models
    Base.metadata.create_all(bind=engine)
