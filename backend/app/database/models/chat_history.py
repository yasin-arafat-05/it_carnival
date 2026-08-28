import uuid
from datetime import datetime
from app.database.base import Base
from typing import List,TYPE_CHECKING
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, mapped_column,Mapped
from sqlalchemy import Text,ForeignKey,DateTime,Index,String,CheckConstraint,Integer,func

if TYPE_CHECKING:
    from app.database.models.user import User


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (
        Index("conversation_idx",'user_id'),
    )
    id : Mapped[int] = mapped_column(Integer,primary_key=True,index=True,autoincrement=True)
    user_id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),ForeignKey("user.id"))
    thread_id: Mapped[str] = mapped_column(Text,nullable=False,unique=True)
    title : Mapped[str] = mapped_column(String(100),nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),default=func.now())

    last_update : Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                     default=func.now(),onupdate=func.now())

    # relationship:
    user : Mapped["User"] = relationship("User",back_populates="conversations")
    message_history: Mapped[List["MessageHistory"]] = relationship("MessageHistory",cascade="all, delete-orphan")


class MessageHistory(Base):
    __tablename__ = "message_history"
    __table_args__ = (
        CheckConstraint("sender_role IN('human','ai')",name="ck_sender_role"),
        Index('message_history_idx','conversation_id'),
    )
    id : Mapped[int] = mapped_column(Integer,primary_key=True,index=True,autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(Integer,ForeignKey("conversations.id"))
    message : Mapped[str] = mapped_column(Text)
    sender_role : Mapped[str] = mapped_column(String(10),nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime(True),default=func.now())

    # relationship:
    conversations: Mapped["Conversation"] = relationship("Conversation",back_populates="message_history")
