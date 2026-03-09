import time
from fastapi import HTTPException
from typing import Optional

from app.planner.query_planner import QueryPlanner
from app.db.session import SessionLocal
from app.ai.intent_service import IntentService
from app.ai.intent_merger import IntentMerger
from app.memory.session_store import session_store
from app.metrics.registry import METRIC_EXECUTORS
from app.core.allowed_fields import (
    ALLOWED_GROUP_BY_FIELDS,
    ALLOWED_FILTER_FIELDS,
    ALLOWED_METRICS
)


class QueryService:

    def __init__(self):
        self.intent_service = IntentService()
        self.merger = IntentMerger()
        self.planner = QueryPlanner()

    def _normalize_intent(self, intent):
        filters = intent.filters or {}

        if "type" in filters and filters["type"]:
            filters["type"] = filters["type"].upper()

        if "priority" in filters and filters["priority"]:
            filters["priority"] = filters["priority"].upper()

        intent.filters = filters

        if intent.date_range:
            if not intent.date_range.start or not intent.date_range.end:
                intent.date_range = None

        return intent

    def execute_query(self, user_query: str, session_id: Optional[str] = None):

        # 1. Load session
        session = session_store.get_or_create(session_id) if session_id else None
        previous_intent = session.get_last_intent() if session else None

        # 2. Extract intent (with previous context if available)
        try:
            incoming_intent = self.intent_service.extract_intent(
                user_query,
                previous_intent=previous_intent
            )
        except Exception:
            # If extraction fails on a follow-up, use previous intent as-is
            incoming_intent = previous_intent if previous_intent else None

        if incoming_intent is None:
            raise HTTPException(status_code=400, detail="Could not extract intent from query")

        # 3. Merge with previous intent
        merged_intent = self.merger.merge(previous_intent, incoming_intent, raw_query=user_query)

        # 4. Plan
        plan = self.planner.plan(merged_intent)

        if plan["execution_type"] != "fast_path":
            raise Exception("Unsupported execution type")

        planned_intent = plan["intent"]

        # 5. Normalize
        planned_intent = self._normalize_intent(planned_intent)

        # 6. Save merged intent back to session
        if session:
            session.update(planned_intent)

        # 7. Derived metric routing
        if "percentage" in user_query.lower():
            from app.metrics.derived_ticket_metrics_executor import DerivedTicketMetricsExecutor

            db = SessionLocal()
            executor = DerivedTicketMetricsExecutor(planned_intent)
            result = executor.execute(db)
            db.close()

            return {
                "intent": planned_intent.model_dump(),
                "execution_path": "derived",
                "result": result
            }

        # 8. Validate metric
        if planned_intent.metric not in ALLOWED_METRICS:
            raise HTTPException(
                status_code=400,
                detail=f"Metric '{planned_intent.metric}' not supported"
            )

        # 9. Validate group_by
        if planned_intent.group_by:
            if planned_intent.group_by not in ALLOWED_GROUP_BY_FIELDS:
                raise HTTPException(
                    status_code=400,
                    detail=f"group_by '{planned_intent.group_by}' not allowed"
                )

        # 10. Validate filters
        filters = planned_intent.filters or {}
        for field in filters.keys():
            if field not in ALLOWED_FILTER_FIELDS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Filter field '{field}' not allowed"
                )

        # 11. Route to executor
        executor_class = METRIC_EXECUTORS.get(planned_intent.metric)
        if not executor_class:
            raise Exception(
                f"No executor found for metric '{planned_intent.metric}'"
            )

        executor = executor_class(planned_intent)
        start_time = time.time()

        db = SessionLocal()
        result = executor.execute(db)
        db.close()

        latency_ms = int((time.time() - start_time) * 1000)

        return {
            "intent": planned_intent.model_dump(),
            "execution_path": plan["execution_type"],
            "latency_ms": latency_ms,
            "result": result
        }