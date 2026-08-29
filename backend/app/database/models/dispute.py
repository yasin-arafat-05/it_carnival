import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, ForeignKey, Index, CheckConstraint, func
from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.user import User
    from app.database.models.transaction import Transaction


class Dispute(Base):
    """
    Dispute & False Transaction Reversal ORM Model.

    Manages mutual false transaction reversal requests and long-process formal complaint investigations.

    Attributes:
        id (UUID): Primary key.
        transaction_id (UUID): Reference transaction ID being disputed.
        sender_id (UUID): Original transfer sender user ID.
        receiver_id (UUID): Original transfer receiver user ID.
        dispute_type (str): Type ('FALSE_TRANSACTION', 'FORMAL_COMPLAINT').
        status (str): Current status ('PENDING_RECEIVER_CONFIRMATION', 'CONFIRMED_BY_RECEIVER', 'UNDER_INVESTIGATION', 'RESOLVED_REVERSED', 'REJECTED').
        reason (str): Reason statement provided by initiator.
        receiver_notes (str): Notes/confirmation text from receiver.
        admin_notes (str): Administrative resolution notes.
        created_at (datetime): UTC creation timestamp.
        updated_at (datetime): UTC timestamp of last status update.
    """

    __tablename__ = "disputes"
    __table_args__ = (
        CheckConstraint(
            "dispute_type IN ('FALSE_TRANSACTION', 'FORMAL_COMPLAINT')",
            name="ck_dispute_type",
        ),
        CheckConstraint(
            "status IN ('PENDING_RECEIVER_CONFIRMATION', 'CONFIRMED_BY_RECEIVER', 'UNDER_INVESTIGATION', 'RESOLVED_REVERSED', 'REJECTED')",
            name="ck_dispute_status",
        ),
        Index("idx_dispute_users", "sender_id", "receiver_id", "status"),
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
    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    receiver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    dispute_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="PENDING_RECEIVER_CONFIRMATION",
        server_default="PENDING_RECEIVER_CONFIRMATION",
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    receiver_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    admin_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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
    transaction: Mapped["Transaction"] = relationship("Transaction", backref="disputes")
    sender: Mapped["User"] = relationship(
        "User", foreign_keys=[sender_id], back_populates="sent_disputes"
    )
    receiver: Mapped["User"] = relationship(
        "User", foreign_keys=[receiver_id], back_populates="received_disputes"
    )
