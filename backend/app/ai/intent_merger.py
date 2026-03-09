from typing import Optional
from app.ai.intent_schema import IntentModel
import copy

COUNT_PRESERVING_PHRASES = [
    "top", "show top", "top n", "limit", "most", "highest", "breakdown"
]

# Phrases that signal the user is starting a fresh analytical direction
PIVOT_PHRASES = [
    "compare", "switch", "instead", "now show", "change to",
    "what about", "how about", "pivot", "across"
]


class IntentMerger:

    def merge(
        self,
        previous: Optional[IntentModel],
        incoming: IntentModel,
        raw_query: str = ""
    ) -> IntentModel:

        if previous is None:
            return incoming

        merged = copy.deepcopy(previous)

        # If incoming has no metric, always inherit from previous
        if previous and not incoming.metric and previous.metric:
            incoming.metric = previous.metric

        # 1. Metric — only replace if incoming differs AND
        #    the raw query isn't just a top_n/limit style request
        if incoming.metric and incoming.metric != previous.metric:
            query_lower = raw_query.lower()
            is_count_preserving = any(
                phrase in query_lower for phrase in COUNT_PRESERVING_PHRASES
            )
            if not is_count_preserving:
                merged.metric = incoming.metric

        # 2. Detect if user is pivoting to a fresh analytical direction
        query_lower = raw_query.lower()
        is_pivot = any(phrase in query_lower for phrase in PIVOT_PHRASES)

        if is_pivot and incoming.group_by and not incoming.filters:
            # User is pivoting — clear stale filters, adopt new group_by
            merged.filters = None
            merged.group_by = incoming.group_by

        elif incoming.filters and len(incoming.filters) > 0:
            # Incoming has explicit filters — patch onto existing
            existing_filters = merged.filters or {}
            existing_filters.update(incoming.filters)
            merged.filters = existing_filters

        elif incoming.group_by and not incoming.filters:
            # User changed group_by only, no filters mentioned
            # Keep existing filters but swap group_by
            merged.group_by = incoming.group_by

        # 3. group_by — replace if incoming has one (and not already handled)
        if incoming.group_by is not None and not is_pivot:
            merged.group_by = incoming.group_by

        # 4. date_range — replace if incoming has one
        if incoming.date_range is not None:
            merged.date_range = incoming.date_range

        # 5. top_n — replace if incoming has one
        if incoming.top_n is not None:
            merged.top_n = incoming.top_n

        # 6. comparison — replace if incoming has one
        if incoming.comparison is not None:
            merged.comparison = incoming.comparison

        # 7. Safety — clear comparison if group_by is now set
        #    (LLM sometimes puts group fields into comparison by mistake)
        if merged.group_by and merged.comparison == merged.group_by:
            merged.comparison = None

        return merged