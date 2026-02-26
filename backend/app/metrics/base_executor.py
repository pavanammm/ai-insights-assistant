from sqlalchemy import text


class BaseMetricExecutor:

    def __init__(self, intent):
        self.intent = intent

    def build_sql(self):
        raise NotImplementedError("Must implement build_sql()")

    def execute(self, db):
        """
        Default execution behavior.
        Child classes should override if needed.
        """
        sql = self.build_sql()
        result = db.execute(text(sql)).fetchone()
        return result[0] if result else None
