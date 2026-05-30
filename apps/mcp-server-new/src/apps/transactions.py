"""
Transactions view — interactive (read-only) table of recent transactions.

Model memanggil tool ini untuk membuka tabel; host me-render DataTable yang
bisa di-search & di-sort sepenuhnya client-side (tidak ada round-trip ke
server setelah render). Untuk query terprogram / filter granular, pakai tool
`read_transactions`.

Styling: pakai theme Presentation (Inter + angka tabular + baris lebih tinggi,
cocok untuk tabel data fokus) dengan accent emerald. Warna amount & badge tipe
pakai semantic token (text-success/text-destructive, variant success/
destructive) supaya ikut theme + dark mode. Catatan: kolom yang berisi
komponen (type badge, amount berwarna) TIDAK di-sort — sorting di cell komponen
tidak bermakna; kolom string (date/payee/account/envelope) tetap sortable.
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

# Tampilkan expense sebagai negatif; income/transfer positif.
_SIGN = {"expense": -1}

# Badge variant per tipe transaksi (semantic token, ikut theme).
_TYPE_VARIANT = {
    "income": "success",
    "expense": "destructive",
    "transfer": "secondary",
}

# Warna teks amount per tipe.
_AMOUNT_CLASS = {
    "income": "text-success",
    "expense": "text-destructive",
    "transfer": "text-muted-foreground",
}


def _format_idr(amount: int, type_: str) -> str:
    signed = amount * _SIGN.get(type_, 1)
    # Pisah ribuan pakai titik (gaya IDR), prefix "Rp".
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
                    "memo": t.memo or "",
                }
                for t in txns
            ]

        with PrefabApp(theme=Presentation(accent="emerald")) as app:
            with Column(gap=4, css_class="p-6"):
                H2("Transactions")
                Muted(f"{len(rows)} most recent")
                if rows:
                    DataTable(
                        columns=[
                            DataTableColumn(key="date", header="Date", sortable=True),
                            DataTableColumn(key="type", header="Type"),
                            DataTableColumn(key="payee", header="Payee", sortable=True),
                            DataTableColumn(
                                key="amount", header="Amount", align="right"
                            ),
                            DataTableColumn(
                                key="account", header="Account", sortable=True
                            ),
                            DataTableColumn(
                                key="envelope", header="Envelope", sortable=True
                            ),
                            DataTableColumn(key="memo", header="Memo"),
                        ],
                        rows=rows,
                        search=True,
                    )
                else:
                    Muted("No transactions yet.")

        return app
