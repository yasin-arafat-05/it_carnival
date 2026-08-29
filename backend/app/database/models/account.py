import uuid
from decimal import Decimal
from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Numeric, DateTime, ForeignKey, CheckConstraint, func
from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.user import User
    from app.database.models.transaction import Transaction
    from app.database.models.ledger import LedgerEntry


class Account(Base):
    """
    Account ORM Model.

    Represents a digital wallet account containing current and available financial balances.
    Enforces non-negative balance check constraints at the database level to prevent overdrafts.

    Attributes:
        id (UUID): Primary key for the account (UUID4).
        user_id (UUID): Foreign key linking 1-to-1 to the owning user.
        account_number (str): Unique financial account identifier string (e.g. ACC-100234).
        balance (Decimal): Total current account balance in BDT (Numeric(18, 2)).
        available_balance (Decimal): Spendable available balance in BDT (Numeric(18, 2)).
        currency (str): Three-letter currency code (Default: 'BDT').
        status (str): Account operational status ('ACTIVE', 'SUSPENDED').
        created_at (datetime): UTC timestamp when account was created.
        updated_at (datetime): UTC timestamp when account balance/status was last modified.

    Relationships:
        user (User): Owning user record.
        sent_transactions (List[Transaction]): Outgoing transfer transactions.
        received_transactions (List[Transaction]): Incoming transfer transactions.
        ledger_entries (List[LedgerEntry]): Audit log of debit/credit double-entry ledger items.
    """

    __tablename__ = "accounts"
    __table_args__ = (
        CheckConstraint("balance >= 0", name="ck_account_balance_non_negative"),
        CheckConstraint("available_balance >= 0", name="ck_account_avail_balance_non_negative"),
        CheckConstraint("status IN ('ACTIVE', 'SUSPENDED')", name="ck_account_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    account_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=Decimal("100000.00"), server_default="100000.00"
    )
    available_balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=Decimal("100000.00"), server_default="100000.00"
    )
    currency: Mapped[str] = mapped_column(
        String(5), nullable=False, default="BDT", server_default="BDT"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="ACTIVE", server_default="ACTIVE"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="account")
    sent_transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        foreign_keys="[Transaction.sender_account_id]",
        back_populates="sender_account",
    )
    received_transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        foreign_keys="[Transaction.receiver_account_id]",
        back_populates="receiver_account",
    )
    ledger_entries: Mapped[List["LedgerEntry"]] = relationship(
        "LedgerEntry", back_populates="account", cascade="all, delete-orphan"
    )
