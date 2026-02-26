from sqlalchemy import text
from app.core.schema_introspection import column_exists


class DerivedTicketMetricsExecutor:

    def __init__(self, intent):
        self.intent = intent

    def execute(self, db):

        # 🔐 Schema validation (make engine schema-aware)
        if not column_exists(db, "tickets", "completed_at"):
            raise Exception(
                "Operational metrics not supported: 'completed_at' column missing."
            )

        # 🔹 Total tickets
        total_sql = """
            SELECT COUNT(*)
            FROM tickets
        """

        # 🔹 Completed within 24 hours
        within_24h_sql = """
            SELECT COUNT(*)
            FROM tickets
            WHERE completed_at IS NOT NULL
            AND julianday(completed_at) - julianday(created_at) <= 1
        """

        total = db.execute(text(total_sql)).scalar()
        within_24h = db.execute(text(within_24h_sql)).scalar()

        percentage = 0
        if total and total > 0:
            percentage = round((within_24h / total) * 100, 2)

        return {
            "total": total,
            "completed_within_24h": within_24h,
            "percentage": percentage
        }