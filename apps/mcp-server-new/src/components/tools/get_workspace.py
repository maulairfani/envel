"""
Discovery tool — panggil sekali di awal session untuk dapat semua akun,
envelope, dan envelope group milik user. Pakai output-nya sebagai context
sepanjang session (LLM ingat ID + nama).

Setelah ada mutasi (account_crud/envelope_crud/plan_action), call ulang
untuk refresh.
"""

from typing import Any

from fastmcp.tools import tool
from sqlalchemy import select

from src.deps import current_user, user_session
from src.models import Account, Envelope, EnvelopeGroup


@tool
def get_workspace() -> dict[str, Any]:
    """Get all accounts, envelopes, and envelope groups for the current user."""
    user = current_user()
    with user_session(user.db_url) as session:
        accounts = (
            session.execute(select(Account).order_by(Account.id)).scalars().all()
        )
        groups = (
            session.execute(
                select(EnvelopeGroup).order_by(
                    EnvelopeGroup.sort_order, EnvelopeGroup.id
                )
            )
            .scalars()
            .all()
        )
        envelopes = (
            session.execute(select(Envelope).order_by(Envelope.id)).scalars().all()
        )

        return {
            "accounts": [
                {"id": a.id, "name": a.name, "type": a.type} for a in accounts
            ],
            "envelope_groups": [
                {"id": g.id, "name": g.name, "sort_order": g.sort_order}
                for g in groups
            ],
            "envelopes": [
                {
                    "id": e.id,
                    "name": e.name,
                    "group_id": e.group_id,
                    "target_type": e.target_type,
                    "target_amount": e.target_amount,
                    "target_date": e.target_date.isoformat() if e.target_date else None,
                }
                for e in envelopes
            ],
        }
