from sqlalchemy import text

def column_exists(db, table_name, column_name):
    result = db.execute(
        text(f"PRAGMA table_info({table_name});")
    ).fetchall()

    return any(row[1] == column_name for row in result)