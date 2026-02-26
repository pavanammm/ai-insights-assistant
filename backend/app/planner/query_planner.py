class QueryPlanner:

    def __init__(self):
        pass

    def plan(self, intent):
        """
        Decide execution strategy based on intent.
        For Phase 4A, always route to fast path.
        """
        return {
            "execution_type": "fast_path",
            "intent": intent
        }
