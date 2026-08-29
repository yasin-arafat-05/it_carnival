from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class MoneyRequestCreate(BaseModel):
    """
    Create Money Request Payload Pydantic Schema.

    Args/Attributes:
        payer_identifier (str): Username, email, or phone number of target payer.
        amount (Decimal): Requested amount (> 0).
        note (Optional[str]): Optional payment request memo.
        expires_in_hours (Optional[int]): Expiration duration in hours (Default: 24, Max: 168).
    """

    payer_identifier: str = Field(
        ...,
        description="Payer username, email, or phone number",
        examples=["yasin_arafat_05"],
    )
    amount: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Requested amount in BDT",
        examples=[1200.00],
    )
    note: Optional[str] = Field(
        None,
        max_length=250,
        description="Optional note for request",
        examples=["Project reimbursement"],
    )
    expires_in_hours: Optional[int] = Field(
        24,
        ge=1,
        le=168,
        description="Expiration time in hours (Default: 24 hours)",
        examples=[24],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "payer_identifier": "yasin_arafat_05",
                "amount": 1200.00,
                "note": "Project reimbursement",
                "expires_in_hours": 24,
            }
        }
    )


class MoneyRequestAction(BaseModel):
    """
    Action Money Request Payload Pydantic Schema.

    Args/Attributes:
        action (Literal['ACCEPT', 'DECLINE']): User action decision.
        idempotency_key (Optional[str]): Key ensuring exact-once execution when accepting.
    """

    action: Literal["ACCEPT", "DECLINE"] = Field(
        ...,
        description="Action to perform on request",
        examples=["ACCEPT"],
    )
    idempotency_key: Optional[str] = Field(
        None,
        max_length=100,
        description="Key for idempotency on accept",
        examples=["REQ_ACCEPT_KEY_99"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "action": "ACCEPT",
                "idempotency_key": "REQ_ACCEPT_KEY_99",
            }
        }
    )


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

    model_config = ConfigDict(from_attributes=True)
