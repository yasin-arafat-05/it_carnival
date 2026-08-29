import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Numeric, DateTime, ForeignKey, Index, CheckConstraint, func
from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.account import Account
    from app.database.models.ledger import LedgerEntry


class Transaction(Base):
    """
    Transaction ORM Model.

    Represents a money transfer event between accounts or initial system funding.
    Includes idempotency protection and readable reference codes.

    Attributes:
        id (UUID): Primary key for the transaction record (UUID4).
        reference_id (str): Human-readable unique reference (e.g. TX-20260829-82931).
        sender_account_id (Optional[UUID]): FK to sender's account (Null for INITIAL_CREDIT).
        receiver_account_id (UUID): FK to receiver's account.
        amount (Decimal): Transaction monetary amount (Numeric(18, 2)). Must be > 0.
        currency (str): Three-letter currency code (Default: 'BDT').
        transaction_type (str): Category ('INITIAL_CREDIT', 'TRANSFER', 'REQUEST_PAYMENT').
        status (str): Processing status ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED').
        idempotency_key (Optional[str]): Client-supplied key ensuring exact-once execution.
        note (Optional[str]): Optional note/memo attached to the money movement.
        created_at (datetime): UTC timestamp of transaction creation.
        updated_at (datetime): UTC timestamp of status modification.

    Relationships:
        sender_account (Optional[Account]): Sender account entity.
        receiver_account (Account): Receiver account entity.
        ledger_entries (List[LedgerEntry]): Balancing DEBIT and CREDIT double-entry ledger entries.
    """

    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_transaction_amount_positive"),
        CheckConstraint(
            "transaction_type IN ('INITIAL_CREDIT', 'TRANSFER', 'REQUEST_PAYMENT')",
            name="ck_transaction_type",
        ),
        CheckConstraint(
            "status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED')",
            name="ck_transaction_status",
        ),
        Index("idx_sender_history", "sender_account_id", "created_at"),
        Index("idx_receiver_history", "receiver_account_id", "created_at"),
        Index("idx_tx_status_date", "status", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    reference_id: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    sender_account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    receiver_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(
        String(5), nullable=False, default="BDT", server_default="BDT"
    )
    transaction_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="PENDING", server_default="PENDING"
    )
    idempotency_key: Mapped[Optional[str]] = mapped_column(
        String(100), unique=True, nullable=True, index=True
    )
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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
    sender_account: Mapped[Optional["Account"]] = relationship(
        "Account",
        foreign_keys="[Transaction.sender_account_id]",
        back_populates="sent_transactions",
    )
    receiver_account: Mapped["Account"] = relationship(
        "Account",
        foreign_keys="[Transaction.receiver_account_id]",
        back_populates="received_transactions",
    )
    ledger_entries: Mapped[List["LedgerEntry"]] = relationship(
        "LedgerEntry", back_populates="transaction", cascade="all, delete-orphan"
    )
