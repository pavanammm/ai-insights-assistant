from sqlalchemy import text
from app.metrics.base_executor import BaseMetricExecutor


class TicketCountExecutor(BaseMetricExecutor):

    def build_sql(self):

        group_by = self.intent.group_by
        filters = self.intent.filters or {}
        date_range = self.intent.date_range

        # 🔹 SELECT SECTION
        if group_by == "month":
            base_sql = """
                SELECT strftime('%Y-%m', created_at) as month, COUNT(*)
                FROM tickets
            """
        elif group_by == "year":
            base_sql = """
                SELECT strftime('%Y', created_at) as year, COUNT(*)
                FROM tickets
            """
        elif group_by == "weekday":
            base_sql = """
                SELECT strftime('%w', created_at) as weekday, COUNT(*)
                FROM tickets
            """
        elif group_by:
            base_sql = f"SELECT {group_by}, COUNT(*) FROM tickets"
        else:
            base_sql = "SELECT COUNT(*) FROM tickets"

        # 🔹 WHERE CONDITIONS
        conditions = []

        if "type" in filters:
            conditions.append(f"type = '{filters['type']}'")

        if "priority" in filters:
            conditions.append(f"priority = '{filters['priority']}'")

        if "state" in filters:
            conditions.append(f"state = '{filters['state']}'")

        if "county" in filters:
            conditions.append(f"county = '{filters['county']}'")

        if "place" in filters:
            conditions.append(f"place = '{filters['place']}'")

        if "work_type" in filters:
            conditions.append(f"work_type = '{filters['work_type']}'")

        if "caller_type" in filters:
            conditions.append(f"caller_type = '{filters['caller_type']}'")

        if "category" in filters:
            conditions.append(f"category = '{filters['category']}'")

        if date_range and date_range.start and date_range.end:
            conditions.append(
                f"DATE(created_at) BETWEEN DATE('{date_range.start}') "
                f"AND DATE('{date_range.end}')"
            )

        if conditions:
            base_sql += " WHERE " + " AND ".join(conditions)

        # 🔹 GROUP BY
        if group_by == "month":
            base_sql += " GROUP BY strftime('%Y-%m', created_at)"
        elif group_by == "year":
            base_sql += " GROUP BY strftime('%Y', created_at)"
        elif group_by == "weekday":
            base_sql += " GROUP BY strftime('%w', created_at)"
        elif group_by:
            base_sql += f" GROUP BY {group_by}"

        # 🔹 RANKING LOGIC (single ORDER BY source of truth)
        if group_by and self.intent.top_n:
            base_sql += " ORDER BY COUNT(*) DESC"
            base_sql += f" LIMIT {self.intent.top_n}"

        return base_sql.strip() + ";"

    # 🔹 EXECUTION LOGIC
    def execute(self, db):

        sql = self.build_sql()

        # Grouped aggregation
        if self.intent.group_by:
            rows = db.execute(text(sql)).fetchall()

            # 🔥 Weekday Mapping for readable output
            if self.intent.group_by == "weekday":
                weekday_map = {
                    "0": "Sunday",
                    "1": "Monday",
                    "2": "Tuesday",
                    "3": "Wednesday",
                    "4": "Thursday",
                    "5": "Friday",
                    "6": "Saturday",
                }

                return [
                    {
                        "weekday": weekday_map.get(str(row[0]), row[0]),
                        "count": row[1]
                    }
                    for row in rows
                ]

            return [
                {
                    self.intent.group_by: row[0],
                    "count": row[1]
                }
                for row in rows
            ]

        # Scalar aggregation
        result = db.execute(text(sql)).fetchone()
        return result[0] if result else None