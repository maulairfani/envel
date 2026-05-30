from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import ForeignKey, UniqueConstraint, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    type: Mapped[str]  # cash | bank | ewallet | credit_card
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP")
    )


class EnvelopeGroup(Base):
    __tablename__ = "envelope_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    sort_order: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP")
    )


class Envelope(Base):
    __tablename__ = "envelopes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    icon: Mapped[str | None]  # nama lucide kebab-case (mis. "utensils"); lucide.dev/icons
    group_id: Mapped[int | None] = mapped_column(ForeignKey("envelope_groups.id"))
    target_type: Mapped[str | None]
    # monthly_spending | monthly_savings | savings_balance | needed_by_date
    target_amount: Mapped[int | None]
    target_date: Mapped[date | None]
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP")
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    envelope_id: Mapped[int | None] = mapped_column(ForeignKey("envelopes.id"))
    type: Mapped[str]  # income | expense | transfer
    amount: Mapped[int]  # IDR, positive; sign tersirat dari type
    date: Mapped[date]
    payee: Mapped[str | None]
    memo: Mapped[str | None]
    transfer_account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"))
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("CURRENT_TIMESTAMP")
    )


class Plan(Base):
    __tablename__ = "plans"
    __table_args__ = (UniqueConstraint("envelope_id", "period"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    envelope_id: Mapped[int] = mapped_column(ForeignKey("envelopes.id"))
    period: Mapped[str]  # YYYY-MM
    assigned: Mapped[int] = mapped_column(default=0)
    carryover: Mapped[int] = mapped_column(default=0)
