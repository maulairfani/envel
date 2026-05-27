from typing import Any

import sqlparse
from fastmcp.tools import tool
from sqlalchemy import text

from src.deps import current_user, user_session

MAX_ROWS = 1000


@tool
def query(sql: str) -> dict[str, Any]:
    """Execute a SQL query against the current user's database."""
    sql = sql.strip()
    if not sql:
        raise ValueError("sql cannot be empty")

    # Single-statement guard — cegah chaining seperti "SELECT 1; DROP TABLE foo"
    statements = [s for s in sqlparse.parse(sql) if str(s).strip()]
    if len(statements) > 1:
        raise ValueError("only one statement allowed per call")

    user = current_user()

    with user_session(user.db_url) as session:
        result = session.execute(text(sql))

        if result.returns_rows:
            rows = result.fetchmany(MAX_ROWS)
            truncated = result.fetchone() is not None
            return {
                "rows": [dict(r._mapping) for r in rows],
                "rowcount": len(rows),
                "truncated": truncated,
            }

        session.commit()
        return {"rows": [], "rowcount": result.rowcount, "truncated": False}
