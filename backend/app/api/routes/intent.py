from fastapi import APIRouter
from app.ai.intent_service import IntentService

router = APIRouter(prefix="/intent", tags=["Intent"])


@router.post("/extract")
def extract_intent(query: str):
    service = IntentService()
    intent = service.extract_intent(query)
    return intent
