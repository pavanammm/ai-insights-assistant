from sqlalchemy import text
from app.metrics.base_executor import BaseMetricExecutor


class TicketListExecutor(BaseMetricExecutor):

    def build_sql(self):

        base_sql = """
        SELECT
            ticket, revision, type, priority, category,
            state, county, place, street, cross_street1, cross_street2,
            caller_type, caller_name, caller_phone, caller_email,
            caller_address, caller_city, caller_state, caller_zip,
            excavator_name, excavator_phone, contact_name, contact_phone, done_for,
            work_type, business_hours, clock_hours, response_required,
            legal_at, work_at, dig_by_at, response_due_at, replace_by_at, expires_at,
            created_at, updated_at, created_by, updated_by
        FROM tickets
        """

        conditions = []
        filters = self.intent.filters or {}

        if "type" in filters:
            conditions.append(f"type = '{filters['type']}'")

        if "priority" in filters:
            conditions.append(f"priority = '{filters['priority']}'")

        if "county" in filters:
            conditions.append(f"county = '{filters['county']}'")

        if "place" in filters:
            conditions.append(f"place = '{filters['place']}'")

        if "state" in filters:
            conditions.append(f"state = '{filters['state']}'")

        if "work_type" in filters:
            conditions.append(f"work_type = '{filters['work_type']}'")

        if "caller_type" in filters:
            conditions.append(f"caller_type = '{filters['caller_type']}'")

        if "category" in filters:
            conditions.append(f"category = '{filters['category']}'")

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
                "index": i + 1,
                "ticket": row[0],
                "revision": row[1],
                "type": row[2],
                "priority": row[3],
                "category": row[4],
                "state": row[5],
                "county": row[6],
                "place": row[7],
                "street": row[8],
                "cross_street1": row[9],
                "cross_street2": row[10],
                "caller_type": row[11],
                "caller_name": row[12],
                "caller_phone": row[13],
                "caller_email": row[14],
                "caller_address": row[15],
                "caller_city": row[16],
                "caller_state": row[17],
                "caller_zip": row[18],
                "excavator_name": row[19],
                "excavator_phone": row[20],
                "contact_name": row[21],
                "contact_phone": row[22],
                "done_for": row[23],
                "work_type": row[24],
                "business_hours": row[25],
                "clock_hours": row[26],
                "response_required": row[27],
                "legal_at": row[28],
                "work_at": row[29],
                "dig_by_at": row[30],
                "response_due_at": row[31],
                "replace_by_at": row[32],
                "expires_at": row[33],
                "created_at": row[34],
                "updated_at": row[35],
                "created_by": row[36],
                "updated_by": row[37],
            }
            for i, row in enumerate(rows)
        ]