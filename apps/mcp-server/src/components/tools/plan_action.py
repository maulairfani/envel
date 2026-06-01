"""
Plan / budget action — assign budget, move money antar envelope, atau
penyesuaian saldo akun.

`assign`: ubah `plans.assigned` untuk envelope di period.
  - mode="set" (default): set ke nilai absolut.
  - mode="add": tambah delta ke nilai sekarang; amount boleh negatif (= kurangi).
`move`: kurangi dari satu envelope, tambah ke envelope lain (atomik).
`adjust_balance`: set saldo sebuah akun ke `target_balance`. Saldo akun itu
  derived dari transaksi, jadi op ini membuat 1 transaksi penyesuaian
  (income/expense, envelope_id=null) sebesar selisihnya. Karena tak ter-assign
  ke envelope mana pun, selisih itu langsung masuk/keluar Ready-to-Assign (RTA).

Semua operations dalam 1 DB transaction. Return menyertakan `ready_to_assign`
(bulan berjalan) terbaru supaya bisa langsung dijelaskan ke user.

Catatan: tool ini TIDAK mengelola `carryover` — itu derived (dihitung saat read
dari (period-1).assigned + (period-1).carryover - activity(period-1)).
"""

import re
from datetime import date as dt_date
from typing import Annotated, Any, Literal, Union

from fastmcp.tools import tool
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import and_, func, select

from src.deps import current_user, user_session
from src.models import Plan, Transaction

from .get_workspace import build_workspace, resolve_period


PERIOD_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def _validate_period(v: str) -> str:
    if not PERIOD_RE.match(v):
        raise ValueError(f"period must match YYYY-MM, got: {v!r}")
    return v


class AssignOp(BaseModel):
    op: Literal["assign"]
    envelope_id: int
    period: str  # YYYY-MM
    amount: int  # mode=set: nilai absolut; mode=add: delta (boleh negatif = kurangi)
    mode: Literal["set", "add"] = "set"

    @field_validator("period")
    @classmethod
    def _check_period(cls, v: str) -> str:
        return _validate_period(v)


class MoveOp(BaseModel):
    op: Literal["move"]
    from_envelope_id: int
    to_envelope_id: int
    period: str
    amount: int  # positif; akan dikurangi dari `from`, ditambah ke `to`

    @field_validator("period")
    @classmethod
    def _check_period(cls, v: str) -> str:
        return _validate_period(v)


class AdjustBalanceOp(BaseModel):
    op: Literal["adjust_balance"]
    account_id: int
    target_balance: int  # set saldo akun ke nilai absolut ini (IDR)


PlanOp = Annotated[
    Union[AssignOp, MoveOp, AdjustBalanceOp], Field(discriminator="op")
]


def _account_balance(session, account_id: int) -> int:
    """Saldo akun saat ini, diturunkan dari transaksi (lihat get_workspace)."""
    rows = session.execute(
        select(Transaction.type, func.coalesce(func.sum(Transaction.amount), 0))
        .where(Transaction.account_id == account_id)
        .group_by(Transaction.type)
    ).all()
    balance = 0
    for t_type, total in rows:
        if t_type == "income":
            balance += total
        elif t_type in ("expense", "transfer"):
            balance -= total
    transfer_in = session.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.type == "transfer",
            Transaction.transfer_account_id == account_id,
        )
    ).scalar_one()
    return balance + transfer_in


@tool
def plan_action(operations: list[PlanOp]) -> dict[str, Any]:
    """Assign budget (op 'assign', mode 'set'=absolute / 'add'=delta; negative add subtracts), move money between envelopes (op 'move'), or set an account balance (op 'adjust_balance' with account_id + target_balance — creates an unassigned adjustment transaction that flows into/out of Ready-to-Assign). Returns the updated ready_to_assign for the current month."""
    if not operations:
        raise ValueError("operations cannot be empty")

    user = current_user()
    affected: dict[tuple[int, str], Plan] = {}
    adjustments: list[dict[str, int]] = []

    with user_session(user.db_url) as session:
        for op in operations:
            if isinstance(op, AssignOp):
                plan = _upsert_plan(session, op.envelope_id, op.period)
                if op.mode == "add":
                    plan.assigned += op.amount  # amount negatif = kurangi
                else:
                    plan.assigned = op.amount
                affected[(plan.envelope_id, plan.period)] = plan
            elif isinstance(op, MoveOp):
                if op.from_envelope_id == op.to_envelope_id:
                    raise ValueError(
                        "from_envelope_id and to_envelope_id must differ"
                    )
                from_plan = _upsert_plan(session, op.from_envelope_id, op.period)
                to_plan = _upsert_plan(session, op.to_envelope_id, op.period)
                from_plan.assigned -= op.amount
                to_plan.assigned += op.amount
                affected[(from_plan.envelope_id, from_plan.period)] = from_plan
                affected[(to_plan.envelope_id, to_plan.period)] = to_plan
            else:  # AdjustBalanceOp
                current = _account_balance(session, op.account_id)
                delta = op.target_balance - current
                if delta != 0:
                    session.add(
                        Transaction(
                            account_id=op.account_id,
                            envelope_id=None,  # tak ter-assign → mengalir ke RTA
                            type="income" if delta > 0 else "expense",
                            amount=abs(delta),
                            date=dt_date.today(),
                            payee="Penyesuaian saldo",
                            memo="Penyesuaian saldo otomatis (plan_action)",
                        )
                    )
                adjustments.append(
                    {
                        "account_id": op.account_id,
                        "previous_balance": current,
                        "new_balance": op.target_balance,
                        "delta": delta,
                    }
                )

        # Flush dulu agar build_workspace melihat perubahan, hitung RTA, lalu commit.
        session.flush()
        ws = build_workspace(session, resolve_period(None))
        session.commit()
        return {
            "plans": [
                {
                    "id": p.id,
                    "envelope_id": p.envelope_id,
                    "period": p.period,
                    "assigned": p.assigned,
                    "carryover": p.carryover,
                }
                for p in affected.values()
            ],
            "balance_adjustments": adjustments,
            "ready_to_assign": ws["ready_to_assign"],
            "summary": ws["summary"],
        }


def _upsert_plan(session, envelope_id: int, period: str) -> Plan:
    stmt = select(Plan).where(
        and_(Plan.envelope_id == envelope_id, Plan.period == period)
    )
    plan = session.execute(stmt).scalar_one_or_none()
    if plan is None:
        plan = Plan(envelope_id=envelope_id, period=period, assigned=0, carryover=0)
        session.add(plan)
        session.flush()
    return plan
