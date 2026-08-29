from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class LedgerEntryResponse(BaseModel):
    """
    Double-Entry Ledger Response Pydantic Schema.

    Args/Attributes:
        id (UUID): Ledger record UUID.
        transaction_id (UUID): Parent transaction UUID.
        account_id (UUID): Affected account UUID.
        entry_type (str): Movement type ('DEBIT' or 'CREDIT').
        amount (Decimal): Entry monetary amount.
        balance_after (Decimal): Account balance snapshot immediately after entry.
        created_at (datetime): Recording timestamp.
    """

    id: UUID
    transaction_id: UUID
    account_id: UUID
    entry_type: str
    amount: Decimal = Field(..., decimal_places=2, description="Ledger entry amount")
    balance_after: Decimal = Field(..., decimal_places=2, description="Balance snapshot after transaction")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
