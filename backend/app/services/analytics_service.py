from sqlalchemy import func
from app.models import Ticket, Response, Dispatch, ResponseDue


class AnalyticsService:

    def __init__(self, db):
        self.db = db

    # 1️⃣ Ticket count by type
    def tickets_by_type(self):
        results = (
            self.db.query(
                Ticket.type,
                func.count(Ticket.id).label("count")
            )
            .group_by(Ticket.type)
            .all()
        )

        return [
            {"type": r.type, "count": r.count}
            for r in results
        ]

    # 2️⃣ Ticket count by priority
    def tickets_by_priority(self):
        results = (
            self.db.query(
                Ticket.priority,
                func.count(Ticket.id).label("count")
            )
            .group_by(Ticket.priority)
            .all()
        )

        return [
            {"priority": r.priority, "count": r.count}
            for r in results
        ]

    # 3️⃣ Member response rate
    def member_response_rate(self):
        dispatch_counts = (
            self.db.query(
                Dispatch.member_uuid,
                func.count(Dispatch.id).label("dispatch_count")
            )
            .group_by(Dispatch.member_uuid)
            .subquery()
        )

        response_counts = (
            self.db.query(
                Response.member_uuid,
                func.count(Response.id).label("response_count")
            )
            .group_by(Response.member_uuid)
            .subquery()
        )

        results = (
            self.db.query(
                dispatch_counts.c.member_uuid,
                dispatch_counts.c.dispatch_count,
                func.coalesce(response_counts.c.response_count, 0).label("response_count")
            )
            .outerjoin(
                response_counts,
                dispatch_counts.c.member_uuid == response_counts.c.member_uuid
            )
            .all()
        )

        output = []
        for r in results:
            rate = 0
            if r.dispatch_count > 0:
                rate = round((r.response_count / r.dispatch_count) * 100, 2)

            output.append({
                "member_uuid": r.member_uuid,
                "dispatch_count": r.dispatch_count,
                "response_count": r.response_count,
                "response_rate_percent": rate
            })

        return output

    # 4️⃣ Overdue SLA count
    def overdue_sla_count(self):
        now = func.datetime("now")

        overdue = (
            self.db.query(func.count(ResponseDue.id))
            .filter(ResponseDue.due_at < func.datetime("now"))
            .scalar()
        )

        return {"overdue_sla_count": overdue}
