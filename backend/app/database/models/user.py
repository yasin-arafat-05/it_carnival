import uuid
from datetime import date
from app.database.base import Base
from typing import Optional,List,TYPE_CHECKING
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import text,String,Text,Date,Index, CheckConstraint

if TYPE_CHECKING:
    from app.database.models.chat_history import Conversation


class User(Base):
    __tablename__ = "user"
    __table_args__ = (
        CheckConstraint("role IN('patient','doctor','admin')",name="ck_role"),
        Index('user_table_idx','id','email'),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(150), unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="patient", server_default="patient")

    #relationship:
    conversations:Mapped[List["Conversation"]] = relationship("Conversation",back_populates="user",
                                                              cascade="all, delete-orphan")  

    
