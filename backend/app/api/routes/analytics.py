from fastapi import APIRouter, Depends
from app.db.session import SessionLocal
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/tickets/by-type")
def tickets_by_type(db=Depends(get_db)):
    service = AnalyticsService(db)
    return service.tickets_by_type()


@router.get("/tickets/by-priority")
def tickets_by_priority(db=Depends(get_db)):
    service = AnalyticsService(db)
    return service.tickets_by_priority()


@router.get("/members/response-rate")
def member_response_rate(db=Depends(get_db)):
    service = AnalyticsService(db)
    return service.member_response_rate()


@router.get("/sla/overdue")
def overdue_sla(db=Depends(get_db)):
    service = AnalyticsService(db)
    return service.overdue_sla_count()
