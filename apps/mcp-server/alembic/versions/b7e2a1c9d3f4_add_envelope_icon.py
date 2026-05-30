"""add envelope icon

Revision ID: b7e2a1c9d3f4
Revises: cc02e71fd150
Create Date: 2026-05-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7e2a1c9d3f4'
down_revision: Union[str, Sequence[str], None] = 'cc02e71fd150'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('envelopes', sa.Column('icon', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('envelopes', 'icon')
