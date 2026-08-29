from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class SendMoneyRequest(BaseModel):
    """
    Send Money Request Payload Pydantic Schema.

    Args/Attributes:
        receiver_identifier (str): Username, email, or phone number of receiver.
        amount (Decimal): Transfer amount (> 0).
        note (Optional[str]): Optional note/memo for payment.
        idempotency_key (Optional[str]): Unique idempotency key to prevent double transfers.
    """

    receiver_identifier: str = Field(
        ...,
        description="Receiver username, email, or phone number",
        examples=["bob_rahman"],
    )
    amount: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Transfer amount in BDT",
        examples=[2500.00],
    )
    note: Optional[str] = Field(
        None,
        max_length=250,
        description="Optional payment note",
        examples=["Lunch payment"],
    )
    idempotency_key: Optional[str] = Field(
        None,
        max_length=100,
        description="Unique key for duplicate prevention",
        examples=["ABC123KEY987"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "receiver_identifier": "bob_rahman",
                "amount": 2500.00,
                "note": "Lunch payment",
                "idempotency_key": "ABC123KEY987",
            }
        }
    )


class TransactionResponse(BaseModel):
    """
    Transaction Details Response Pydantic Schema.

    Args/Attributes:
        id (UUID): Transaction record UUID.
        reference_id (str): Public reference identifier (e.g. TX-20260829-82931).
        sender_account_id (Optional[UUID]): Sender account UUID (None for INITIAL_CREDIT).
        receiver_account_id (UUID): Receiver account UUID.
        sender_username (Optional[str]): Username of sender.
        receiver_username (Optional[str]): Username of receiver.
        amount (Decimal): Monetary transfer amount.
        currency (str): Three-letter currency code ('BDT').
        transaction_type (str): Type ('INITIAL_CREDIT', 'TRANSFER', 'REQUEST_PAYMENT').
        status (str): Status ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED').
        idempotency_key (Optional[str]): Idempotency key if supplied.
        note (Optional[str]): Attached transaction note.
        created_at (datetime): Creation timestamp.
    """

    id: UUID
    reference_id: str
    sender_account_id: Optional[UUID] = None
    receiver_account_id: UUID
    sender_username: Optional[str] = None
    receiver_username: Optional[str] = None
    amount: Decimal = Field(..., decimal_places=2)
    currency: str
    transaction_type: str
    status: str
    idempotency_key: Optional[str] = None
    note: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
