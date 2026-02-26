from sqlalchemy import text
from app.metrics.base_executor import BaseMetricExecutor


class TicketListExecutor(BaseMetricExecutor):

    def build_sql(self):

        base_sql = """
        SELECT ticket, revision, type, priority, created_at
        FROM tickets
        """

        conditions = []
        filters = self.intent.filters or {}

        if "type" in filters:
            conditions.append(f"type = '{filters['type']}'")

        if "priority" in filters:
            conditions.append(f"priority = '{filters['priority']}'")

        date_range = self.intent.date_range
        if date_range and date_range.start and date_range.end:
            conditions.append(
                f"DATE(created_at) BETWEEN DATE('{date_range.start}') "
                f"AND DATE('{date_range.end}')"
            )

        if conditions:
            base_sql += " WHERE " + " AND ".join(conditions)

        base_sql += " ORDER BY created_at DESC"

        if self.intent.top_n:
            base_sql += f" LIMIT {int(self.intent.top_n)}"

        return base_sql + ";"

    def execute(self, db):
        sql = self.build_sql()
        rows = db.execute(text(sql)).fetchall()

        return [
            {
                "ticket": row[0],
                "revision": row[1],
                "type": row[2],
                "priority": row[3],
                "created_at": row[4],
            }
            for row in rows
        ]