"""
Account CRUD — create/update/delete one account per call.

Listing accounts is done via `get_workspace` (there is no 'list' action here).
"""

from typing import Annotated, Any, Literal, Union

from fastmcp.tools import tool
from pydantic import BaseModel, Field

from src.deps import current_user, user_session
from src.models import Account


AccountType = Literal["cash", "bank", "ewallet", "credit_card"]


class CreateAccountOp(BaseModel):
    action: Literal["create"]
    name: str
    type: AccountType


class UpdateAccountOp(BaseModel):
    action: Literal["update"]
    id: int
    name: str | None = None
    type: AccountType | None = None


class DeleteAccountOp(BaseModel):
    action: Literal["delete"]
    id: int


AccountOp = Annotated[
    Union[CreateAccountOp, UpdateAccountOp, DeleteAccountOp],
    Field(discriminator="action"),
]


@tool
def account_crud(payload: AccountOp) -> dict[str, Any]:
    """Create, update, or delete an account."""
    user = current_user()
    with user_session(user.db_url) as session:
        if isinstance(payload, CreateAccountOp):
            account = Account(name=payload.name, type=payload.type)
            session.add(account)
            session.commit()
            return {"id": account.id, "name": account.name, "type": account.type}

        if isinstance(payload, UpdateAccountOp):
            account = session.get(Account, payload.id)
            if not account:
                raise ValueError(f"account id={payload.id} not found")
            if payload.name is not None:
                account.name = payload.name
            if payload.type is not None:
                account.type = payload.type
            session.commit()
            return {"id": account.id, "name": account.name, "type": account.type}

        # DeleteAccountOp
        account = session.get(Account, payload.id)
        if not account:
            raise ValueError(f"account id={payload.id} not found")
        session.delete(account)
        session.commit()
        return {"ok": True, "deleted_id": payload.id}
