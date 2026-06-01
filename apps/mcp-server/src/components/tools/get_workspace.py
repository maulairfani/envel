"""
Discovery tool — call once at the start of a session to get all of the user's
accounts, envelopes, and envelope groups ALONG WITH their money positions. Use
its output as context throughout the session (the LLM remembers ID + name + budget).

After any mutation (account_crud/envelope_crud/plan_action/write_transactions),
call again to refresh.

Money figures (all IDR, integer) are derived from `transactions` + `plans`
(the new schema stores neither account balances nor carryover):

  balance(account)      = Σ income_in − Σ expense_out − Σ transfer_out + Σ transfer_in
  total_balance         = Σ balance(account)  (transfers between accounts cancel out)
  activity(env, period) = Σ expense amount for that envelope in that month
  carryover(env, P)     = max(0, available(env, P-1))   ← clamped ≥0, derived
  available(env, P)     = carryover + assigned(env, P) − activity(env, P)
  ready_to_assign       = total_balance − Σ available(env, P)

`period` defaults to the current month (YYYY-MM).
"""

import re
from datetime import date as dt_date
from typing import Annotated, Any

from fastmcp.tools import tool
from pydantic import Field
from sqlalchemy import func, select

from src.deps import current_user, user_session
from src.models import Account, Envelope, EnvelopeGroup, Plan, Transaction

PERIOD_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def _current_period() -> str:
    return dt_date.today().strftime("%Y-%m")


def _available_at(
    assigned_by_period: dict[str, int],
    activity_by_period: dict[str, int],
    target: str,
) -> tuple[int, int, int]:
    """Compute (assigned, activity, available) for one envelope at the `target` period.

    Carryover is derived by telescoping: iterate over all periods with data
    (assigned or activity) that are <= target in chronological order, clamping to >=0
    at each month rollover. Periods without data only carry the carryover forward.
    """
    periods = sorted(set(assigned_by_period) | set(activity_by_period))
    carry = 0
    available = 0
    seen_target = False
    for p in periods:
        if p > target:  # string compare is safe for zero-padded YYYY-MM
            break
        a = assigned_by_period.get(p, 0)
        act = activity_by_period.get(p, 0)
        available = carry + a - act
        if p == target:
            seen_target = True
        carry = max(0, available)  # carryover flows into the next period
    if not seen_target:
        # target has no data → available = incoming carryover (+0 −0)
        available = carry
    return (
        assigned_by_period.get(target, 0),
        activity_by_period.get(target, 0),
        available,
    )


def resolve_period(period: str | None) -> str:
    if period is not None and not PERIOD_RE.match(period):
        raise ValueError(f"period must match YYYY-MM, got: {period!r}")
    return period or _current_period()


def build_workspace(session, target: str) -> dict[str, Any]:
    """Compute the workspace snapshot (accounts+balance, envelopes+available, RTA).

    Split out from the tool so it can be reused by the app UI (envelopes snapshot).
    """
    accounts = (
        session.execute(select(Account).order_by(Account.id)).scalars().all()
    )
    groups = (
        session.execute(
            select(EnvelopeGroup).order_by(EnvelopeGroup.sort_order, EnvelopeGroup.id)
        )
        .scalars()
        .all()
    )
    envelopes = (
        session.execute(select(Envelope).order_by(Envelope.id)).scalars().all()
    )

    # ── Balance per account: aggregate amount per (account_id, type) + incoming transfers ──
    bal_rows = session.execute(
        select(
            Transaction.account_id,
            Transaction.type,
            func.coalesce(func.sum(Transaction.amount), 0),
        ).group_by(Transaction.account_id, Transaction.type)
    ).all()
    transfer_in_rows = session.execute(
        select(
            Transaction.transfer_account_id,
            func.coalesce(func.sum(Transaction.amount), 0),
        )
        .where(
            Transaction.type == "transfer",
            Transaction.transfer_account_id.is_not(None),
        )
        .group_by(Transaction.transfer_account_id)
    ).all()

    balance: dict[int, int] = {a.id: 0 for a in accounts}
    for acct_id, t_type, total in bal_rows:
        if acct_id is None:
            continue
        if t_type == "income":
            balance[acct_id] = balance.get(acct_id, 0) + total
        elif t_type in ("expense", "transfer"):
            balance[acct_id] = balance.get(acct_id, 0) - total
    for acct_id, total in transfer_in_rows:
        balance[acct_id] = balance.get(acct_id, 0) + total

    total_balance = sum(balance.values())

    # ── assigned per (envelope, period) from plans ──
    plan_rows = session.execute(
        select(Plan.envelope_id, Plan.period, Plan.assigned)
    ).all()
    assigned_map: dict[int, dict[str, int]] = {}
    for env_id, p, amt in plan_rows:
        assigned_map.setdefault(env_id, {})[p] = amt

    # ── activity (expense) per (envelope, period) ──
    period_expr = func.to_char(Transaction.date, "YYYY-MM")
    act_rows = session.execute(
        select(
            Transaction.envelope_id,
            period_expr,
            func.coalesce(func.sum(Transaction.amount), 0),
        )
        .where(
            Transaction.type == "expense",
            Transaction.envelope_id.is_not(None),
        )
        .group_by(Transaction.envelope_id, period_expr)
    ).all()
    activity_map: dict[int, dict[str, int]] = {}
    for env_id, p, amt in act_rows:
        activity_map.setdefault(env_id, {})[p] = amt

    # ── available per envelope at the target period ──
    envelope_out = []
    total_available = 0
    for e in envelopes:
        assigned, activity, available = _available_at(
            assigned_map.get(e.id, {}), activity_map.get(e.id, {}), target
        )
        total_available += available
        envelope_out.append(
            {
                "id": e.id,
                "name": e.name,
                "icon": e.icon,
                "group_id": e.group_id,
                "target_type": e.target_type,
                "target_amount": e.target_amount,
                "target_date": e.target_date.isoformat() if e.target_date else None,
                "assigned": assigned,
                "activity": activity,
                "available": available,
            }
        )

    ready_to_assign = total_balance - total_available

    return {
        "period": target,
        "accounts": [
            {"id": a.id, "name": a.name, "type": a.type, "balance": balance[a.id]}
            for a in accounts
        ],
        "envelope_groups": [
            {"id": g.id, "name": g.name, "sort_order": g.sort_order} for g in groups
        ],
        "envelopes": envelope_out,
        "summary": {
            "total_balance": total_balance,
            "total_available": total_available,
            "ready_to_assign": ready_to_assign,
            "is_balanced": abs(ready_to_assign) < 1,
            "is_overspent": ready_to_assign < -1,
        },
        "ready_to_assign": ready_to_assign,
    }


@tool
def get_workspace(
    period: Annotated[
        str | None,
        Field(default=None, description="Budget period YYYY-MM (default: current month)"),
    ] = None,
) -> dict[str, Any]:
    """Get accounts, envelopes, groups, balances, and ready-to-assign."""
    target = resolve_period(period)
    user = current_user()
    with user_session(user.db_url) as session:
        return build_workspace(session, target)
