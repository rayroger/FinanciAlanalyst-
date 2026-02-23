"""SQLAlchemy ORM models: User, Account, Transaction."""

import uuid
from datetime import datetime, date

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    accounts: Mapped[list["Account"]] = relationship("Account", back_populates="user")


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Plaid item / account identifiers
    plaid_item_id: Mapped[str] = mapped_column(String(255), nullable=False)
    plaid_account_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    # SECURITY: access_token stored encrypted (Fernet) — never log this field
    encrypted_access_token: Mapped[str] = mapped_column(Text, nullable=False)
    institution_name: Mapped[str | None] = mapped_column(String(255))
    account_name: Mapped[str | None] = mapped_column(String(255))
    account_type: Mapped[str | None] = mapped_column(String(64))
    account_subtype: Mapped[str | None] = mapped_column(String(64))
    cursor: Mapped[str | None] = mapped_column(Text)  # Plaid sync cursor
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="accounts")
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="account"
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    plaid_transaction_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    # Plaid: positive = debit (expense), negative = credit (income)
    is_credit: Mapped[bool] = mapped_column(Boolean, default=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    merchant_name: Mapped[str | None] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    category: Mapped[str | None] = mapped_column(String(128), index=True)
    plaid_category: Mapped[str | None] = mapped_column(String(255))
    pending: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    account: Mapped["Account"] = relationship("Account", back_populates="transactions")
