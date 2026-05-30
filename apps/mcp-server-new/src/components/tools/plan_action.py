"""
Plan / budget action — assign budget atau move money antar envelope.

`assign`: ubah `plans.assigned` untuk envelope di period.
  - mode="set" (default): set ke nilai absolut.
  - mode="add": tambah delta ke nilai sekarang; amount boleh negatif (= kurangi).
`move`: kurangi dari satu envelope, tambah ke envelope lain (atomik).

Semua operations dalam 1 DB transaction.

Catatan: tool ini TIDAK mengelola `carryover` — itu derived (dihitung saat read
dari (period-1).assigned + (period-1).carryover - activity(period-1)).
"""

import re
from typing import Annotated, Any, Literal, Union

from fastmcp.tools import tool
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import and_, select

from src.deps import current_user, user_session
from src.models import Plan


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


PlanOp = Annotated[Union[AssignOp, MoveOp], Field(discriminator="op")]


@tool
def plan_action(operations: list[PlanOp]) -> dict[str, Any]:
    """Assign budget (mode 'set'=absolute, 'add'=delta; negative add subtracts) or move money between envelopes atomically."""
    if not operations:
        raise ValueError("operations cannot be empty")

    user = current_user()
    affected: dict[tuple[int, str], Plan] = {}

    with user_session(user.db_url) as session:
        for op in operations:
            if isinstance(op, AssignOp):
                plan = _upsert_plan(session, op.envelope_id, op.period)
                if op.mode == "add":
                    plan.assigned += op.amount  # amount negatif = kurangi
                else:
                    plan.assigned = op.amount
                affected[(plan.envelope_id, plan.period)] = plan
            else:  # MoveOp
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
            ]
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
