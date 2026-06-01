"""
Transactions view — interactive (read-only) table of recent transactions.

The model calls this tool to open the table; the host renders a DataTable that
can be searched & sorted entirely client-side (no round-trip to the
server after render). For programmatic queries / granular filtering, use the
`read_transactions` tool.

Styling: uses the Presentation theme (Inter + tabular numbers + taller rows,
suited to focused data tables). Amount colors & type badges
use semantic tokens (text-success/text-destructive, variant success/
destructive) so they follow the theme + dark mode. Note: columns containing
components (type badge, colored amount) are NOT sorted — sorting on component
cells is meaningless; string columns (date/payee/account/envelope) stay sortable.
"""

from typing import Annotated

from fastmcp import FastMCP
from prefab_ui.app import PrefabApp
from prefab_ui.components import (
    Badge,
    Column,
    DataTable,
    DataTableColumn,
    H2,
    Muted,
    Span,
)
from prefab_ui.themes import Presentation
from pydantic import Field
from sqlalchemy import select

from src.deps import current_user, user_session
from src.models import Account, Envelope, Transaction

DEFAULT_LIMIT = 200
MAX_LIMIT = 1000

# Show expense as negative; income/transfer positive.
_SIGN = {"expense": -1}

# Badge variant per transaction type (semantic token, follows theme).
_TYPE_VARIANT = {
    "income": "success",
    "expense": "destructive",
    "transfer": "secondary",
}

# Amount text color per type.
_AMOUNT_CLASS = {
    "income": "text-success",
    "expense": "text-destructive",
    "transfer": "text-muted-foreground",
}


def _format_idr(amount: int, type_: str) -> str:
    signed = amount * _SIGN.get(type_, 1)
    # Separate thousands with a dot (IDR style), prefix "Rp".
    return f"Rp {signed:,}".replace(",", ".")


def register(mcp: FastMCP) -> None:
    @mcp.tool(app=True)
    def transactions_view(
        limit: Annotated[
            int, Field(ge=1, le=MAX_LIMIT, description="Max rows to show")
        ] = DEFAULT_LIMIT,
    ) -> PrefabApp:
        """Open an interactive, searchable table of recent transactions."""
        user = current_user()
        with user_session(user.db_url) as session:
            accounts = {
                a.id: a.name
                for a in session.execute(select(Account)).scalars().all()
            }
            envelopes = {
                e.id: e.name
                for e in session.execute(select(Envelope)).scalars().all()
            }
            txns = (
                session.execute(
                    select(Transaction)
                    .order_by(Transaction.date.desc(), Transaction.id.desc())
                    .limit(limit)
                )
                .scalars()
                .all()
            )

            rows = [
                {
                    "date": t.date.isoformat(),
                    "type": Badge(
                        t.type, variant=_TYPE_VARIANT.get(t.type, "secondary")
                    ),
                    "payee": t.payee or "",
                    "amount": Span(
                        _format_idr(t.amount, t.type),
                        css_class=[
                            _AMOUNT_CLASS.get(t.type, ""),
                            "tabular-nums font-medium",
                        ],
                    ),
                    "account": accounts.get(t.account_id, f"#{t.account_id}"),
                    "envelope": (
                        envelopes.get(t.envelope_id, f"#{t.envelope_id}")
                        if t.envelope_id is not None
                        else ""
                    ),
                }
                for t in txns
            ]

        with PrefabApp(theme=Presentation()) as app:
            with Column(gap=4, css_class="p-6 w-full"):
                H2("Transactions")
                Muted(f"{len(rows)} most recent")
                if rows:
                    DataTable(
                        css_class="w-full",
                        columns=[
                            DataTableColumn(key="date", header="Date", sortable=True),
                            DataTableColumn(key="type", header="Type"),
                            DataTableColumn(key="payee", header="Payee", sortable=True),
                            DataTableColumn(
                                key="amount", header="Amount", align="right"
                            ),
                            DataTableColumn(
                                key="envelope", header="Envelope", sortable=True
                            ),
                        ],
                        rows=rows,
                        search=True,
                        paginated=True,
                        page_size=8,
                    )
                else:
                    Muted("No transactions yet.")

        return app
