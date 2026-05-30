"""
Envelope CRUD — create/update/delete satu envelope per call.

List dilakukan via `get_workspace`.
"""

from datetime import date
from typing import Annotated, Any, Literal, Union

from fastmcp.tools import tool
from pydantic import BaseModel, Field

from src.deps import current_user, user_session
from src.models import Envelope


TargetType = Literal[
    "spend_monthly",  # belanja sampai X/bulan, refill ke target (sisa ngegulung)
    "save_monthly",   # sisihkan X tiap bulan, numpuk tanpa akhir
    "save_total",     # kumpulkan sampai X total, tanpa tanggal
    "save_by_date",   # kumpulkan X sebelum target_date
]


class CreateEnvelopeOp(BaseModel):
    action: Literal["create"]
    name: str
    icon: str | None = Field(
        default=None,
        description="Lucide icon name, kebab-case (e.g. 'utensils', 'car', 'home'). See lucide.dev/icons.",
    )
    group_id: int | None = None
    target_type: TargetType | None = None
    target_amount: int | None = None
    target_date: date | None = None


class UpdateEnvelopeOp(BaseModel):
    action: Literal["update"]
    id: int
    name: str | None = None
    icon: str | None = Field(
        default=None,
        description="Lucide icon name, kebab-case (e.g. 'utensils', 'car', 'home'). See lucide.dev/icons.",
    )
    group_id: int | None = None
    target_type: TargetType | None = None
    target_amount: int | None = None
    target_date: date | None = None


class DeleteEnvelopeOp(BaseModel):
    action: Literal["delete"]
    id: int


EnvelopeOp = Annotated[
    Union[CreateEnvelopeOp, UpdateEnvelopeOp, DeleteEnvelopeOp],
    Field(discriminator="action"),
]


@tool
def envelope_crud(payload: EnvelopeOp) -> dict[str, Any]:
    """Create, update, or delete an envelope."""
    user = current_user()
    with user_session(user.db_url) as session:
        if isinstance(payload, CreateEnvelopeOp):
            envelope = Envelope(
                name=payload.name,
                icon=payload.icon,
                group_id=payload.group_id,
                target_type=payload.target_type,
                target_amount=payload.target_amount,
                target_date=payload.target_date,
            )
            session.add(envelope)
            session.commit()
            return _envelope_dict(envelope)

        if isinstance(payload, UpdateEnvelopeOp):
            envelope = session.get(Envelope, payload.id)
            if not envelope:
                raise ValueError(f"envelope id={payload.id} not found")
            data = payload.model_dump(exclude_unset=True, exclude={"action", "id"})
            for k, v in data.items():
                setattr(envelope, k, v)
            session.commit()
            return _envelope_dict(envelope)

        # DeleteEnvelopeOp
        envelope = session.get(Envelope, payload.id)
        if not envelope:
            raise ValueError(f"envelope id={payload.id} not found")
        session.delete(envelope)
        session.commit()
        return {"ok": True, "deleted_id": payload.id}


def _envelope_dict(e: Envelope) -> dict[str, Any]:
    return {
        "id": e.id,
        "name": e.name,
        "icon": e.icon,
        "group_id": e.group_id,
        "target_type": e.target_type,
        "target_amount": e.target_amount,
        "target_date": e.target_date.isoformat() if e.target_date else None,
    }
