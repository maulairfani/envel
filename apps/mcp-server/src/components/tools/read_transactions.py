"""
Read transactions dengan filter lengkap.

Default ordering: date DESC, id DESC (transaksi terbaru paling atas).
Default limit 100, max 1000.
"""

from datetime import date as dt_date
from typing import Any, Literal

from fastmcp.tools import tool
from sqlalchemy import and_, select

from src.deps import current_user, user_session
from src.models import Transaction


MAX_LIMIT = 1000


@tool
def read_transactions(
    envelope_id: int | None = None,
    account_id: int | None = None,
    type: Literal["income", "expense", "transfer"] | None = None,
    date_from: dt_date | None = None,
    date_to: dt_date | None = None,
    payee_contains: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    """Query transactions with optional filters."""
    if limit < 1 or limit > MAX_LIMIT:
        raise ValueError(f"limit must be between 1 and {MAX_LIMIT}")
    if offset < 0:
        raise ValueError("offset must be >= 0")

    conditions = []
    if envelope_id is not None:
        conditions.append(Transaction.envelope_id == envelope_id)
    if account_id is not None:
        # Match account_id ATAU transfer_account_id (untuk transfer)
        from sqlalchemy import or_
        conditions.append(
            or_(
                Transaction.account_id == account_id,
                Transaction.transfer_account_id == account_id,
            )
        )
    if type is not None:
        conditions.append(Transaction.type == type)
    if date_from is not None:
        conditions.append(Transaction.date >= date_from)
    if date_to is not None:
        conditions.append(Transaction.date <= date_to)
    if payee_contains:
        conditions.append(Transaction.payee.ilike(f"%{payee_contains}%"))

    user = current_user()
    with user_session(user.db_url) as session:
        stmt = (
            select(Transaction)
            .where(and_(*conditions) if conditions else True)
            .order_by(Transaction.date.desc(), Transaction.id.desc())
            .limit(limit + 1)  # fetch +1 untuk deteksi has_more
            .offset(offset)
        )
        rows = session.execute(stmt).scalars().all()

        has_more = len(rows) > limit
        rows = rows[:limit]

        return {
            "transactions": [
                {
                    "id": t.id,
                    "type": t.type,
                    "account_id": t.account_id,
                    "envelope_id": t.envelope_id,
                    "transfer_account_id": t.transfer_account_id,
                    "amount": t.amount,
                    "date": t.date.isoformat(),
                    "payee": t.payee,
                    "memo": t.memo,
                }
                for t in rows
            ],
            "rowcount": len(rows),
            "has_more": has_more,
        }
