from typing import Any

from fastmcp.tools import tool
from sqlalchemy import text

from src.deps import current_user, user_session


@tool
def query(sql: str) -> dict[str, Any]:
    """Execute a SQL query against the current user's database."""
    sql = sql.strip()
    if not sql:
        raise ValueError("sql cannot be empty")

    user = current_user()

    with user_session(user.db_path) as session:
        result = session.execute(text(sql))

        if result.returns_rows:
            rows = [dict(row._mapping) for row in result.fetchall()]
            return {"rows": rows, "rowcount": len(rows)}

        session.commit()
        return {"rows": [], "rowcount": result.rowcount}
