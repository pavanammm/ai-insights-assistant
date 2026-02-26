import time
from fastapi import HTTPException

from app.planner.query_planner import QueryPlanner
from app.db.session import SessionLocal
from app.ai.intent_service import IntentService
from app.metrics.registry import METRIC_EXECUTORS
from app.core.allowed_fields import (
    ALLOWED_GROUP_BY_FIELDS,
    ALLOWED_FILTER_FIELDS,
    ALLOWED_METRICS
)


class QueryService:

    def __init__(self):
        self.intent_service = IntentService()
        self.planner = QueryPlanner()

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

        # 🔹 Normalize date_range safety
        if intent.date_range:
            if not intent.date_range.start or not intent.date_range.end:
                intent.date_range = None

        return intent

    def execute_query(self, user_query: str):

        # 1️⃣ Extract intent
        intent = self.intent_service.extract_intent(user_query)

        # 2️⃣ Planning layer
        plan = self.planner.plan(intent)

        if plan["execution_type"] != "fast_path":
            raise Exception("Unsupported execution type")

        planned_intent = plan["intent"]

        # 3️⃣ Normalize intent AFTER planning
        planned_intent = self._normalize_intent(planned_intent)

        # 🔥 🔥 🔥 MINIMAL DERIVED METRIC ROUTING
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

        # 🔐 Enforce Metric Validation
        if planned_intent.metric not in ALLOWED_METRICS:
            raise HTTPException(
                status_code=400,
                detail=f"Metric '{planned_intent.metric}' not supported"
            )

        # 🔐 Validate group_by field
        if planned_intent.group_by:
            if planned_intent.group_by not in ALLOWED_GROUP_BY_FIELDS:
                raise HTTPException(
                    status_code=400,
                    detail=f"group_by '{planned_intent.group_by}' not allowed"
                )

        # 🔐 Validate filter fields
        filters = planned_intent.filters or {}

        for field in filters.keys():
            if field not in ALLOWED_FILTER_FIELDS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Filter field '{field}' not allowed"
                )

        # 5️⃣ Route to Metric Executor
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