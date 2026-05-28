"""
Bulk write transactions — create/update/delete dalam 1 call, atomik per call.

Semua operasi dalam satu DB transaction: kalau ada satu yang gagal,
keseluruhan rollback. Cocok untuk import dari struk (banyak baris sekaligus)
atau koreksi multi-row.

Untuk transfer, `amount` selalu positif. `account_id` adalah sumber,
`transfer_account_id` adalah tujuan. Sign uang ditentukan oleh `type` saat
dihitung balance.
"""

from datetime import date as dt_date
from typing import Annotated, Any, Literal, Union

from fastmcp.tools import tool
from pydantic import BaseModel, Field

from src.deps import current_user, user_session
from src.models import Transaction


TxType = Literal["income", "expense", "transfer"]


class CreateExpense(BaseModel):
    op: Literal["create_expense"]
    account_id: int
    envelope_id: int | None = None
    amount: int  # IDR, positif
    date: dt_date
    payee: str | None = None
    memo: str | None = None


class CreateIncome(BaseModel):
    op: Literal["create_income"]
    account_id: int
    envelope_id: int | None = None  # nullable: income tanpa kategori = Ready To Assign
    amount: int
    date: dt_date
    payee: str | None = None
    memo: str | None = None


class CreateTransfer(BaseModel):
    op: Literal["create_transfer"]
    account_id: int  # sumber
    transfer_account_id: int  # tujuan
    amount: int
    date: dt_date
    memo: str | None = None


class UpdateTransaction(BaseModel):
    op: Literal["update"]
    id: int
    # Semua field optional — partial update via exclude_unset
    type: TxType | None = None
    account_id: int | None = None
    envelope_id: int | None = None
    amount: int | None = None
    date: dt_date | None = None
    payee: str | None = None
    memo: str | None = None
    transfer_account_id: int | None = None


class DeleteTransaction(BaseModel):
    op: Literal["delete"]
    id: int


TxOp = Annotated[
    Union[CreateExpense, CreateIncome, CreateTransfer, UpdateTransaction, DeleteTransaction],
    Field(discriminator="op"),
]


@tool
def write_transactions(operations: list[TxOp]) -> dict[str, Any]:
    """Bulk create/update/delete transactions atomically (single DB transaction)."""
    if not operations:
        raise ValueError("operations cannot be empty")

    user = current_user()
    created: list[dict[str, Any]] = []
    updated: list[int] = []
    deleted: list[int] = []

    with user_session(user.db_url) as session:
        for op in operations:
            if isinstance(op, CreateExpense):
                tx = Transaction(
                    account_id=op.account_id,
                    envelope_id=op.envelope_id,
                    type="expense",
                    amount=op.amount,
                    date=op.date,
                    payee=op.payee,
                    memo=op.memo,
                )
                session.add(tx)
                session.flush()
                created.append({"id": tx.id, "type": "expense"})

            elif isinstance(op, CreateIncome):
                tx = Transaction(
                    account_id=op.account_id,
                    envelope_id=op.envelope_id,
                    type="income",
                    amount=op.amount,
                    date=op.date,
                    payee=op.payee,
                    memo=op.memo,
                )
                session.add(tx)
                session.flush()
                created.append({"id": tx.id, "type": "income"})

            elif isinstance(op, CreateTransfer):
                tx = Transaction(
                    account_id=op.account_id,
                    transfer_account_id=op.transfer_account_id,
                    type="transfer",
                    amount=op.amount,
                    date=op.date,
                    memo=op.memo,
                )
                session.add(tx)
                session.flush()
                created.append({"id": tx.id, "type": "transfer"})

            elif isinstance(op, UpdateTransaction):
                tx = session.get(Transaction, op.id)
                if not tx:
                    raise ValueError(f"transaction id={op.id} not found")
                changes = op.model_dump(exclude_unset=True, exclude={"op", "id"})
                for k, v in changes.items():
                    setattr(tx, k, v)
                updated.append(op.id)

            else:  # DeleteTransaction
                tx = session.get(Transaction, op.id)
                if not tx:
                    raise ValueError(f"transaction id={op.id} not found")
                session.delete(tx)
                deleted.append(op.id)

        session.commit()

    return {"created": created, "updated": updated, "deleted": deleted}
