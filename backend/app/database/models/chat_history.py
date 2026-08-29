import uuid
from datetime import datetime
from app.database.base import Base
from typing import List, TYPE_CHECKING
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy import Text, ForeignKey, DateTime, Index, String, CheckConstraint, Integer, func

if TYPE_CHECKING:
    from app.database.models.user import User


class Conversation(Base):
    """
    Conversation ORM Model.

    Represents an LLM/Chat conversation session associated with a user.

    Attributes:
        id (int): Primary key autoincrement integer.
        user_id (UUID): Foreign key referencing users.id.
        thread_id (str): Unique thread identifier.
        title (str): Conversation title.
        created_at (datetime): UTC creation timestamp.
        last_update (datetime): UTC timestamp of last update.

    Relationships:
        user (User): Owner user entity.
        message_history (List[MessageHistory]): Conversation message history items.
    """

    __tablename__ = "conversations"
    __table_args__ = (
        Index("conversation_idx", "user_id"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    thread_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), server_default=func.now())
    last_update: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now(), onupdate=func.now()
    )

    # Relationship:
    user: Mapped["User"] = relationship("User", back_populates="conversations")
    message_history: Mapped[List["MessageHistory"]] = relationship("MessageHistory", back_populates="conversations", cascade="all, delete-orphan")


class MessageHistory(Base):
    """
    MessageHistory ORM Model.

    Represents individual messages in a conversation thread.

    Attributes:
        id (int): Primary key autoincrement integer.
        conversation_id (int): Foreign key referencing conversations.id.
        message (str): Message content text.
        sender_role (str): Role of sender ('human' or 'ai').
        created_at (datetime): UTC creation timestamp.

    Relationships:
        conversations (Conversation): Parent conversation instance.
    """

    __tablename__ = "message_history"
    __table_args__ = (
        CheckConstraint("sender_role IN('human','ai')", name="ck_sender_role"),
        Index("message_history_idx", "conversation_id"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    sender_role: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), server_default=func.now())

    # Relationship:
    conversations: Mapped["Conversation"] = relationship("Conversation", back_populates="message_history")
