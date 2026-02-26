def build_ticket_count_sql(intent):

    base_sql = "SELECT COUNT(*) FROM tickets"
    conditions = []

    filters = intent.filters or {}
    date_range = intent.date_range

    ticket_type = filters.get("type")
    if ticket_type:
        conditions.append(f"type = '{ticket_type}'")

    priority = filters.get("priority")
    if priority:
        conditions.append(f"priority = '{priority}'")

    if date_range == "today":
        conditions.append("DATE(created_at) = DATE('now')")

    if conditions:
        base_sql += " WHERE " + " AND ".join(conditions)

    base_sql += ";"

    return base_sql


def build_ticket_list_sql(intent):

    limit = intent.top_n or 10

    base_sql = """
        SELECT id, ticket, type, priority, created_at
        FROM tickets
    """

    conditions = []
    filters = intent.filters or {}

    ticket_type = filters.get("type")
    if ticket_type:
        conditions.append(f"type = '{ticket_type}'")

    priority = filters.get("priority")
    if priority:
        conditions.append(f"priority = '{priority}'")

    if conditions:
        base_sql += " WHERE " + " AND ".join(conditions)

    base_sql += " ORDER BY created_at DESC"
    base_sql += f" LIMIT {limit};"

    return base_sql
