import uuid
from decimal import Decimal
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Numeric, DateTime, ForeignKey, Index, CheckConstraint, func
from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.transaction import Transaction
    from app.database.models.account import Account


class LedgerEntry(Base):
    """
    LedgerEntry ORM Model.

    Represents an immutable double-entry bookkeeping ledger record.
    Every successful transaction generates balancing DEBIT and CREDIT entries.

    Attributes:
        id (UUID): Primary key identifier (UUID4).
        transaction_id (UUID): Foreign key referencing the parent transaction.
        account_id (UUID): Foreign key referencing the affected account.
        entry_type (str): Type of movement ('DEBIT' for decrease, 'CREDIT' for increase).
        amount (Decimal): Amount of money transferred in this entry (Numeric(18, 2)).
        balance_after (Decimal): Account balance snapshot immediately after entry execution.
        created_at (datetime): UTC timestamp of entry recording.

    Relationships:
        transaction (Transaction): Parent transaction object.
        account (Account): Target account object.
    """

    __tablename__ = "ledger_entries"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_ledger_amount_positive"),
        CheckConstraint("entry_type IN ('DEBIT', 'CREDIT')", name="ck_ledger_entry_type"),
        Index("idx_account_ledger", "account_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    entry_type: Mapped[str] = mapped_column(String(10), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), server_default=func.now()
    )

    # Relationships
    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="ledger_entries")
    account: Mapped["Account"] = relationship("Account", back_populates="ledger_entries")
