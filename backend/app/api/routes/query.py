from fastapi import APIRouter
from app.services.query_service import QueryService

router = APIRouter()

service = QueryService()


@router.post("/query")
def run_query(query: str):
    return service.execute_query(query)
