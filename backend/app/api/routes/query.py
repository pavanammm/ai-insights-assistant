from fastapi import APIRouter
from typing import Optional
from app.services.query_service import QueryService

router = APIRouter()

service = QueryService()


@router.post("/query")
def run_query(query: str, session_id: Optional[str] = None):
    return service.execute_query(query, session_id=session_id)