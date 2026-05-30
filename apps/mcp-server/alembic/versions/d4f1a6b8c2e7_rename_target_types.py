"""rename envelope target_type values to spend/save scheme

monthly_spending -> spend_monthly
monthly_savings  -> save_monthly
savings_balance  -> save_total
needed_by_date   -> save_by_date

Revision ID: d4f1a6b8c2e7
Revises: b7e2a1c9d3f4
Create Date: 2026-05-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'd4f1a6b8c2e7'
down_revision: Union[str, Sequence[str], None] = 'b7e2a1c9d3f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_RENAME = {
    "monthly_spending": "spend_monthly",
    "monthly_savings": "save_monthly",
    "savings_balance": "save_total",
    "needed_by_date": "save_by_date",
}


def _apply(mapping: dict[str, str]) -> None:
    for old, new in mapping.items():
        op.execute(
            f"UPDATE envelopes SET target_type = '{new}' "
            f"WHERE target_type = '{old}'"
        )


def upgrade() -> None:
    _apply(_RENAME)


def downgrade() -> None:
    _apply({new: old for old, new in _RENAME.items()})
