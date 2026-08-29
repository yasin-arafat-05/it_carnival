import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, Index, CheckConstraint, func
from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.account import Account
    from app.database.models.notification import Notification
    from app.database.models.money_request import MoneyRequest
    from app.database.models.chat_history import Conversation
    from app.database.models.dispute import Dispute


class User(Base):
    """
    User ORM Model.

    Represents a registered user identity in the EduManage digital wallet system.
    Supports authentication, role-based authorization ('USER', 'ADMIN'), and profile search.

    Attributes:
        id (UUID): Unique primary key identifier (UUID4).
        full_name (str): Full display name of the user (max 150 characters).
        username (str): Unique alphanumeric username for profile search and login.
        phone_number (str): Unique contact phone number.
        email (str): Unique email address for authentication and communication.
        password_hash (str): Secure Argon2id hashed password string.
        role (str): Role for authorization ('USER', 'ADMIN').
        account_status (str): Current status of the user ('ACTIVE', 'SUSPENDED', 'BLOCKED').
        created_at (datetime): UTC timestamp when the user registered.
        updated_at (datetime): UTC timestamp when the user record was last modified.

    Relationships:
        account (Account): 1-to-1 digital wallet account owned by the user.
        notifications (List[Notification]): List of in-app notifications for this user.
        sent_money_requests (List[MoneyRequest]): Money requests sent by this user.
        received_money_requests (List[MoneyRequest]): Money requests sent to this user.
        sent_disputes (List[Dispute]): Reversal requests / disputes initiated by this user.
        received_disputes (List[Dispute]): Reversal requests / disputes targeting this user.
        conversations (List[Conversation]): LLM conversation history threads owned by this user.
    """

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("account_status IN ('ACTIVE', 'SUSPENDED', 'BLOCKED')", name="ck_user_account_status"),
        CheckConstraint("role IN ('USER', 'ADMIN')", name="ck_user_role"),
        Index("idx_user_auth", "email", "username", "phone_number"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default="USER", server_default="USER"
    )
    account_status: Mapped[str] = mapped_column(
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
    account: Mapped[Optional["Account"]] = relationship(
        "Account", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    sent_money_requests: Mapped[List["MoneyRequest"]] = relationship(
        "MoneyRequest",
        foreign_keys="[MoneyRequest.requester_id]",
        back_populates="requester",
        cascade="all, delete-orphan",
    )
    received_money_requests: Mapped[List["MoneyRequest"]] = relationship(
        "MoneyRequest",
        foreign_keys="[MoneyRequest.payer_id]",
        back_populates="payer",
        cascade="all, delete-orphan",
    )
    sent_disputes: Mapped[List["Dispute"]] = relationship(
        "Dispute",
        foreign_keys="[Dispute.sender_id]",
        back_populates="sender",
        cascade="all, delete-orphan",
    )
    received_disputes: Mapped[List["Dispute"]] = relationship(
        "Dispute",
        foreign_keys="[Dispute.receiver_id]",
        back_populates="receiver",
        cascade="all, delete-orphan",
    )
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation", back_populates="user", cascade="all, delete-orphan"
    )
