from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict


class AccountResponse(BaseModel):
    """
    Financial Account Response Pydantic Schema.

    Args/Attributes:
        id (UUID): Account unique UUID.
        user_id (UUID): Owning user UUID.
        account_number (str): Account identifier string.
        balance (Decimal): Total balance in BDT.
        available_balance (Decimal): Available spendable balance in BDT.
        currency (str): Currency string code ('BDT').
        status (str): Account status ('ACTIVE', 'SUSPENDED').
        created_at (datetime): Account creation timestamp.
    """

    id: UUID
    user_id: UUID
    account_number: str
    balance: Decimal = Field(..., decimal_places=2, description="Total balance in BDT")
    available_balance: Decimal = Field(..., decimal_places=2, description="Available spendable balance in BDT")
    currency: str = Field(..., description="Currency code")
    status: str = Field(..., description="Account status")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WalletDashboardResponse(BaseModel):
    """
    Wallet Dashboard Overview Response Pydantic Schema.

    Args/Attributes:
        account (AccountResponse): Account balance and status summary.
        recent_transactions (List[dict]): List of recent money transactions.
    """

    account: AccountResponse
    recent_transactions: List[dict] = Field(default_factory=list, description="Recent transaction history items")

    model_config = ConfigDict(from_attributes=True)
