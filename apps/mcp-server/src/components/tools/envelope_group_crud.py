"""
Envelope group CRUD — create/update/delete one group per call.

Listing is done via `get_workspace`.
"""

from typing import Annotated, Any, Literal, Union

from fastmcp.tools import tool
from pydantic import BaseModel, Field

from src.deps import current_user, user_session
from src.models import EnvelopeGroup


class CreateGroupOp(BaseModel):
    action: Literal["create"]
    name: str
    sort_order: int = 0


class UpdateGroupOp(BaseModel):
    action: Literal["update"]
    id: int
    name: str | None = None
    sort_order: int | None = None


class DeleteGroupOp(BaseModel):
    action: Literal["delete"]
    id: int


GroupOp = Annotated[
    Union[CreateGroupOp, UpdateGroupOp, DeleteGroupOp],
    Field(discriminator="action"),
]


@tool
def envelope_group_crud(payload: GroupOp) -> dict[str, Any]:
    """Create, update, or delete an envelope group."""
    user = current_user()
    with user_session(user.db_url) as session:
        if isinstance(payload, CreateGroupOp):
            group = EnvelopeGroup(name=payload.name, sort_order=payload.sort_order)
            session.add(group)
            session.commit()
            return {
                "id": group.id,
                "name": group.name,
                "sort_order": group.sort_order,
            }

        if isinstance(payload, UpdateGroupOp):
            group = session.get(EnvelopeGroup, payload.id)
            if not group:
                raise ValueError(f"envelope_group id={payload.id} not found")
            if payload.name is not None:
                group.name = payload.name
            if payload.sort_order is not None:
                group.sort_order = payload.sort_order
            session.commit()
            return {
                "id": group.id,
                "name": group.name,
                "sort_order": group.sort_order,
            }

        # DeleteGroupOp
        group = session.get(EnvelopeGroup, payload.id)
        if not group:
            raise ValueError(f"envelope_group id={payload.id} not found")
        session.delete(group)
        session.commit()
        return {"ok": True, "deleted_id": payload.id}
