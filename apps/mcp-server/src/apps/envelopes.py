"""
Envelopes snapshot — interactive (read-only) status of each envelope per group.

Purpose: quickly scan the position of each budget and immediately see which
envelopes are overspent. "Overspent" = `available < 0` (spent more than is available
in the envelope, including carryover). Each envelope = one Card (progress bar
spent vs budget + semantic color), grouped per group (the group becomes a heading
section). The summary on top counts how many are overspent.

The numbers are derived from `build_workspace` (same as the get_workspace tool) so
the RTA/available logic isn't duplicated.
"""

from datetime import datetime
from typing import Annotated, Any

from fastmcp import FastMCP
from prefab_ui.app import PrefabApp
from prefab_ui.components import (
    Alert,
    AlertDescription,
    Badge,
    Card,
    CardContent,
    Column,
    H2,
    H3,
    Icon,
    Muted,
    Progress,
    Row,
    Span,
    Text,
)
from prefab_ui.themes import Presentation
from pydantic import Field

from src.components.tools.get_workspace import build_workspace, resolve_period
from src.deps import current_user, user_session


def _idr(amount: int) -> str:
    return f"Rp {amount:,}".replace(",", ".")


def _period_label(period: str) -> str:
    """'2026-05' → 'May 2026'."""
    return datetime.strptime(period, "%Y-%m").strftime("%B %Y")


def _avail_color(available: int) -> str:
    if available < 0:
        return "text-destructive"
    if available > 0:
        return "text-success"
    return "text-muted-foreground"


def _envelope_card(env: dict[str, Any]) -> None:
    """Render one envelope as a Card: name + available + spent/budget progress."""
    activity = env["activity"]
    available = env["available"]
    budget = available + activity  # = carryover + assigned (money in the envelope this month)
    overspent = available < 0

    if budget > 0:
        prog_max, prog_val = budget, activity
        variant = "destructive" if overspent else "success"
    elif activity > 0:  # spending without budget → fully overspent
        prog_max, prog_val = activity, activity
        variant = "destructive"
    else:  # not assigned yet & no activity yet
        prog_max, prog_val = 1, 0
        variant = "muted"

    with Card():
        with CardContent(css_class="px-4 py-2"):
            with Column(gap=1, css_class="w-full"):
                with Row(css_class="justify-between items-center w-full gap-2"):
                    with Row(css_class="items-center gap-2 min-w-0"):
                        if env.get("icon"):
                            Icon(name=env["icon"], size="sm")
                        Text(env["name"], css_class="font-medium truncate")
                        if overspent:
                            Badge("Overspent", variant="destructive")
                    Span(
                        _idr(available),
                        css_class=[
                            _avail_color(available),
                            "tabular-nums font-medium shrink-0",
                        ],
                    )
                Progress(value=prog_val, max=prog_max, variant=variant, size="sm")
                Muted(f"{_idr(activity)} of {_idr(budget)}", css_class="text-xs")


def _render(ws: dict[str, Any]) -> PrefabApp:
    target = ws["period"]
    envelopes = ws["envelopes"]
    groups = ws["envelope_groups"]
    rta = ws["ready_to_assign"]
    overspent_count = sum(1 for e in envelopes if e["available"] < 0)

    # envelopes per group_id (None = ungrouped)
    by_group: dict[Any, list[dict]] = {}
    for e in envelopes:
        by_group.setdefault(e["group_id"], []).append(e)

    # order: groups by sort_order, then ungrouped at the end
    sections = [(g["id"], g["name"]) for g in groups if g["id"] in by_group]
    if None in by_group:
        sections.append((None, "Ungrouped"))

    with PrefabApp(theme=Presentation()) as app:
        with Column(gap=6, css_class="p-6 w-full"):
            with Column(gap=2, css_class="w-full"):
                H2("Envelopes")
                with Row(gap=2, align="center", css_class="w-full"):
                    Muted(_period_label(target))
                    if overspent_count:
                        Badge(f"{overspent_count} overspent", variant="destructive")
                # RTA is only shown when non-zero — emphasized via Alert.
                if rta > 0:
                    with Alert(variant="info"):
                        AlertDescription(
                            f"{_idr(rta)} ready to assign — give it a job in your envelopes."
                        )
                elif rta < 0:
                    with Alert(variant="destructive"):
                        AlertDescription(
                            f"{_idr(-rta)} over-assigned — pull money back from some envelopes to cover it."
                        )

            if not envelopes:
                Muted("No envelopes yet.")
            for group_id, group_name in sections:
                items = by_group.get(group_id, [])
                group_available = sum(e["available"] for e in items)
                with Column(gap=3, css_class="w-full"):
                    with Row(css_class="justify-between items-center w-full"):
                        H3(group_name)
                        Span(
                            _idr(group_available),
                            css_class=[_avail_color(group_available), "tabular-nums"],
                        )
                    with Column(gap=3, css_class="w-full"):
                        for env in items:
                            _envelope_card(env)

    return app


def register(mcp: FastMCP) -> None:
    @mcp.tool(app=True)
    def envelopes_view(
        period: Annotated[
            str | None,
            Field(default=None, description="Budget period YYYY-MM (default: current month)"),
        ] = None,
    ) -> PrefabApp:
        """Open a snapshot of every envelope's status, flagging overspent ones."""
        target = resolve_period(period)
        user = current_user()
        with user_session(user.db_url) as session:
            ws = build_workspace(session, target)
        return _render(ws)
