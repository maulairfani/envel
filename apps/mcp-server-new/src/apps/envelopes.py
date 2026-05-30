"""
Envelopes snapshot — interactive (read-only) status tiap envelope per group.

Tujuan: scan cepat posisi tiap budget dan langsung kelihatan envelope mana yang
overspent. "Overspent" = `available < 0` (sudah belanja lebih dari yang tersedia
di envelope, termasuk carryover). Tiap envelope punya progress bar
(spent vs budget) + warna semantik; ringkasan di atas menghitung berapa yang
overspent.

Angka diturunkan dari `build_workspace` (sama dengan tool get_workspace) supaya
logika RTA/available tidak terduplikasi.
"""

from typing import Annotated, Any

from fastmcp import FastMCP
from prefab_ui.app import PrefabApp
from prefab_ui.components import (
    Badge,
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    Column,
    H2,
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


def _avail_color(available: int) -> str:
    if available < 0:
        return "text-destructive"
    if available > 0:
        return "text-success"
    return "text-muted-foreground"


def _envelope_block(env: dict[str, Any]) -> None:
    """Render satu envelope: nama + available + progress bar spent/budget."""
    activity = env["activity"]
    available = env["available"]
    budget = available + activity  # = carryover + assigned (uang di envelope bln ini)
    overspent = available < 0

    if budget > 0:
        prog_max, prog_val = budget, activity
        variant = "destructive" if overspent else "success"
    elif activity > 0:  # belanja tanpa budget → overspent penuh
        prog_max, prog_val = activity, activity
        variant = "destructive"
    else:  # belum di-assign & belum ada aktivitas
        prog_max, prog_val = 1, 0
        variant = "muted"

    with Column(gap=1, css_class="w-full"):
        with Row(css_class="justify-between items-center w-full"):
            Text(env["name"], css_class="font-medium")
            Span(
                _idr(available),
                css_class=[_avail_color(available), "tabular-nums font-medium"],
            )
        Progress(value=prog_val, max=prog_max, variant=variant, size="sm")
        with Row(css_class="justify-between items-center w-full"):
            Muted(f"{_idr(activity)} of {_idr(budget)} spent")
            if overspent:
                Badge("Overspent", variant="destructive")


def _render(ws: dict[str, Any]) -> PrefabApp:
    target = ws["period"]
    envelopes = ws["envelopes"]
    groups = ws["envelope_groups"]
    rta = ws["ready_to_assign"]
    overspent_count = sum(1 for e in envelopes if e["available"] < 0)

    # envelope per group_id (None = ungrouped)
    by_group: dict[Any, list[dict]] = {}
    for e in envelopes:
        by_group.setdefault(e["group_id"], []).append(e)

    # urutan: groups sesuai sort_order, lalu ungrouped di akhir
    sections = [(g["id"], g["name"]) for g in groups if g["id"] in by_group]
    if None in by_group:
        sections.append((None, "Ungrouped"))

    with PrefabApp(theme=Presentation(accent="emerald")) as app:
        with Column(gap=4, css_class="p-6"):
            H2("Envelopes")
            with Row(gap=3, align="center", css_class="w-full"):
                Muted(target)
                if overspent_count:
                    Badge(f"{overspent_count} overspent", variant="destructive")
                else:
                    Badge("All on track", variant="success")
                Muted(f"Ready to assign: {_idr(rta)}")

            if not envelopes:
                Muted("No envelopes yet.")
            for group_id, group_name in sections:
                items = by_group.get(group_id, [])
                group_available = sum(e["available"] for e in items)
                with Card():
                    with CardHeader():
                        with Row(css_class="justify-between items-center w-full"):
                            CardTitle(group_name)
                            Span(
                                _idr(group_available),
                                css_class=[
                                    _avail_color(group_available),
                                    "tabular-nums",
                                ],
                            )
                    with CardContent():
                        with Column(gap=4, css_class="w-full"):
                            for env in items:
                                _envelope_block(env)

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
