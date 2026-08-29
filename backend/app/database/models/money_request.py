import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Numeric, DateTime, ForeignKey, Index, CheckConstraint, func
from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.user import User


class MoneyRequest(Base):
    """
    MoneyRequest ORM Model.

    Represents a payment request initialized by one user targeting another user.
    Tracks status updates ('PENDING', 'ACCEPTED', 'DECLINED', 'EXPIRED') and expiration times.

    Attributes:
        id (UUID): Primary key of the money request (UUID4).
        requester_id (UUID): FK referencing the user requesting funds.
        payer_id (UUID): FK referencing the targeted user asked to pay.
        amount (Decimal): Monetary amount requested in BDT (Numeric(18, 2)).
        note (Optional[str]): Optional message attached to the request.
        status (str): Current request lifecycle status ('PENDING', 'ACCEPTED', 'DECLINED', 'EXPIRED').
        expires_at (datetime): UTC timestamp after which the request automatically expires.
        created_at (datetime): UTC timestamp of request issuance.
        updated_at (datetime): UTC timestamp of status transition.

    Relationships:
        requester (User): Requester user instance.
        payer (User): Payer user instance.
    """

    __tablename__ = "money_requests"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_money_request_amount_positive"),
        CheckConstraint(
            "status IN ('PENDING', 'ACCEPTED', 'DECLINED', 'EXPIRED')",
            name="ck_money_request_status",
        ),
        Index("idx_pending_requests", "payer_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    requester_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    payer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="PENDING", server_default="PENDING"
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
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
    requester: Mapped["User"] = relationship(
        "User",
        foreign_keys="[MoneyRequest.requester_id]",
        back_populates="sent_money_requests",
    )
    payer: Mapped["User"] = relationship(
        "User",
        foreign_keys="[MoneyRequest.payer_id]",
        back_populates="received_money_requests",
    )
