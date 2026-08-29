from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class MoneyRequestCreate(BaseModel):
    """
    Create Money Request Payload Pydantic Schema.

    Args/Attributes:
        payer_identifier (str): Username, email, or phone number of target payer.
        amount (Decimal): Requested amount (> 0).
        note (Optional[str]): Optional payment request memo.
    """

    payer_identifier: str = Field(..., description="Payer username, email, or phone number")
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Requested amount in BDT")
    note: Optional[str] = Field(None, max_length=250, description="Optional note for request")


class MoneyRequestAction(BaseModel):
    """
    Action Money Request Payload Pydantic Schema.

    Args/Attributes:
        action (Literal['ACCEPT', 'DECLINE']): User action decision.
        idempotency_key (Optional[str]): Key ensuring exact-once execution when accepting.
    """

    action: Literal["ACCEPT", "DECLINE"] = Field(..., description="Action to perform on request")
    idempotency_key: Optional[str] = Field(None, max_length=100, description="Key for idempotency on accept")


class MoneyRequestResponse(BaseModel):
    """
    Money Request Details Response Pydantic Schema.

    Args/Attributes:
        id (UUID): Request item UUID.
        requester_id (UUID): Requester user UUID.
        payer_id (UUID): Payer user UUID.
        requester_name (Optional[str]): Name of requester.
        payer_name (Optional[str]): Name of target payer.
        amount (Decimal): Requested amount.
        note (Optional[str]): Attached note.
        status (str): Request status ('PENDING', 'ACCEPTED', 'DECLINED', 'EXPIRED').
        expires_at (datetime): Request expiration timestamp.
        created_at (datetime): Creation timestamp.
    """

    id: UUID
    requester_id: UUID
    payer_id: UUID
    requester_name: Optional[str] = None
    payer_name: Optional[str] = None
    amount: Decimal = Field(..., decimal_places=2)
    note: Optional[str] = None
    status: str
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
