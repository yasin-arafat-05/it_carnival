from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class FalseTransactionRequest(BaseModel):
    """
    False Transaction Reversal Request Pydantic Schema.

    Args/Attributes:
        transaction_reference (str): Transaction reference ID (e.g. TX-20260829-6A9824).
        reason (str): Reason statement detailing the mistake.
    """

    transaction_reference: str = Field(
        ...,
        description="Reference ID of the accidental transfer",
        examples=["TX-20260829-6A9824"],
    )
    reason: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Reason statement for false transaction reversal",
        examples=["Accidentally sent money to wrong recipient handle"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "transaction_reference": "TX-20260829-6A9824",
                "reason": "Accidentally sent money to wrong recipient handle",
            }
        }
    )


class ComplaintRequest(BaseModel):
    """
    Formal Complaint Filing Pydantic Schema.

    Args/Attributes:
        transaction_reference (str): Reference ID of disputed transaction.
        reason (str): Detailed complaint description.
    """

    transaction_reference: str = Field(
        ...,
        description="Reference ID of transaction under dispute",
        examples=["TX-20260829-6A9824"],
    )
    reason: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Detailed complaint statement for long-process investigation",
        examples=["Receiver refuses to acknowledge receipt after wrong transfer"],
    )


class DisputeReceiverAction(BaseModel):
    """
    Receiver Confirmation Pydantic Schema for False Transactions.

    Args/Attributes:
        action (Literal['CONFIRM', 'DENY']): Receiver decision.
        notes (Optional[str]): Receiver confirmation notes.
    """

    action: Literal["CONFIRM", "DENY"] = Field(
        ...,
        description="Receiver confirmation action",
        examples=["CONFIRM"],
    )
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Notes from receiver",
        examples=["I confirm I received this transfer by mistake"],
    )


class DisputeResolveAction(BaseModel):
    """
    Admin Dispute Resolution Pydantic Schema.

    Args/Attributes:
        decision (Literal['APPROVE_REVERSAL', 'REJECT']): Admin resolution decision.
        admin_notes (Optional[str]): Admin explanation/notes.
    """

    decision: Literal["APPROVE_REVERSAL", "REJECT"] = Field(
        ...,
        description="Administrative decision",
        examples=["APPROVE_REVERSAL"],
    )
    admin_notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Administrative investigation notes",
        examples=["Approved after reviewing receiver confirmation"],
    )


class DisputeResponse(BaseModel):
    """
    Dispute & False Transaction Item Response Pydantic Schema.

    Args/Attributes:
        id (UUID): Dispute ID.
        transaction_id (UUID): Disputed transaction UUID.
        transaction_reference (Optional[str]): Transaction reference ID.
        sender_id (UUID): Sender user ID.
        receiver_id (UUID): Receiver user ID.
        sender_username (Optional[str]): Username of sender.
        receiver_username (Optional[str]): Username of receiver.
        amount (Decimal): Amount involved in dispute.
        dispute_type (str): Type ('FALSE_TRANSACTION', 'FORMAL_COMPLAINT').
        status (str): Current status ('PENDING_RECEIVER_CONFIRMATION', 'CONFIRMED_BY_RECEIVER', 'UNDER_INVESTIGATION', 'RESOLVED_REVERSED', 'REJECTED').
        reason (str): Reason statement.
        receiver_notes (Optional[str]): Receiver response notes.
        admin_notes (Optional[str]): Admin resolution notes.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
    """

    id: UUID
    transaction_id: UUID
    transaction_reference: Optional[str] = None
    sender_id: UUID
    receiver_id: UUID
    sender_username: Optional[str] = None
    receiver_username: Optional[str] = None
    amount: Decimal = Field(..., decimal_places=2)
    dispute_type: str
    status: str
    reason: str
    receiver_notes: Optional[str] = None
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
