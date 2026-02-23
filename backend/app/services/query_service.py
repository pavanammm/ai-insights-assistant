import time
from sqlalchemy import text
from app.db.session import SessionLocal
from app.ai.intent_service import IntentService
from app.core.metrics import ALLOWED_METRICS
from app.services.fast_path_builders import (
    build_ticket_count_sql,
    build_ticket_list_sql
)

FAST_PATH_BUILDERS = {
    "ticket_count": build_ticket_count_sql,
    "ticket_list": build_ticket_list_sql
}


class QueryService:

    def __init__(self):
        self.intent_service = IntentService()

    # 🔹 Minimal & Safe Normalization
    def _normalize_intent(self, intent):

        # Ensure filters is always a dict
        filters = intent.filters or {}

        # Normalize type
        if "type" in filters and filters["type"]:
            filters["type"] = filters["type"].upper()

        # Normalize priority
        if "priority" in filters and filters["priority"]:
            filters["priority"] = filters["priority"].upper()

        intent.filters = filters
        return intent

    def execute_query(self, user_query: str):

        # Step 1 — Extract intent (Pydantic model)
        intent = self.intent_service.extract_intent(user_query)

        # Step 2 — Normalize intent
        intent = self._normalize_intent(intent)

        # 🔐 Step 3 — Enforce Metric Validation
        if intent.metric not in ALLOWED_METRICS:
            raise Exception(f"Metric '{intent.metric}' not supported in Fast Path")

        # Step 4 — Fast path routing via builder
        builder = FAST_PATH_BUILDERS.get(intent.metric)

        if not builder:
            raise Exception(f"No Fast Path builder for metric '{intent.metric}'")

        sql = builder(intent)

        # Step 5 — Execute SQL
        start_time = time.time()

        db = SessionLocal()
        result = db.execute(text(sql)).fetchone()
        db.close()

        latency_ms = int((time.time() - start_time) * 1000)

        return {
            "intent": intent.model_dump(),
            "execution_path": "fast",
            "sql": sql,
            "latency_ms": latency_ms,
            "result": {
                "value": result[0] if result else None
            }
        }

    # Example: Inside any fast-path builder (e.g., build_ticket_count_sql)
    # Structured DateRange handling:
    # if date_range and date_range.start and date_range.end:
    #     conditions.append(
    #         f"DATE(created_at) BETWEEN DATE('{date_range.start}') "
    #         f"AND DATE('{date_range.end}')"
    #     )
