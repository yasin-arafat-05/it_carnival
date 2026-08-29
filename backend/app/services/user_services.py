import uuid
from decimal import Decimal
from datetime import datetime
from typing import List
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User
from app.database.models.account import Account
from app.database.models.transaction import Transaction
from app.database.models.ledger import LedgerEntry
from app.database.models.notification import Notification
from app.database.schemas.user import UserResponse, UserSearchResponse

INITIAL_BALANCE = Decimal("100000.00")


async def get_current_user_profile(user: User, db: AsyncSession) -> UserResponse:
    """
    Returns the profile information of the current authenticated user along with their digital wallet account.
    If the user was created prior to automatic funding logic, automatically provisions an Account with BDT 100,000.

    Args:
        user (User): Authenticated user object.
        db (AsyncSession): Database session.

    Returns:
        UserResponse: Profile response schema including account balance details.
    """
    # Query user with eagerly loaded account
    query = select(User).where(User.id == user.id).options(selectinload(User.account))
    result = await db.execute(query)
    db_user = result.scalar_one_or_none() or user

    # Auto-provision initial BDT 100,000 account if user registered before wallet system was added
    if db_user.account is None:
        account_no = f"ACC-{uuid.uuid4().hex[:8].upper()}"
        new_account = Account(
            user_id=db_user.id,
            account_number=account_no,
            balance=INITIAL_BALANCE,
            available_balance=INITIAL_BALANCE,
            currency="BDT",
            status="ACTIVE",
        )
        db.add(new_account)
        await db.flush()

        now_str = datetime.utcnow().strftime("%Y%m%d")
        tx_ref = f"TX-{now_str}-{uuid.uuid4().hex[:6].upper()}"
        initial_tx = Transaction(
            reference_id=tx_ref,
            sender_account_id=None,
            receiver_account_id=new_account.id,
            amount=INITIAL_BALANCE,
            currency="BDT",
            transaction_type="INITIAL_CREDIT",
            status="COMPLETED",
            note="Initial account registration credit funding",
        )
        db.add(initial_tx)
        await db.flush()

        ledger_entry = LedgerEntry(
            transaction_id=initial_tx.id,
            account_id=new_account.id,
            entry_type="CREDIT",
            amount=INITIAL_BALANCE,
            balance_after=INITIAL_BALANCE,
        )
        db.add(ledger_entry)

        welcome_notif = Notification(
            user_id=db_user.id,
            title="Account Funded",
            message=f"Welcome to your Digital Wallet! Your account has been credited with BDT {INITIAL_BALANCE:,.2f} initial balance.",
            notification_type="INITIAL_CREDIT",
            reference_id=tx_ref,
        )
        db.add(welcome_notif)

        await db.commit()
        await db.refresh(db_user)

    return UserResponse.model_validate(db_user)


async def search_users(
    query: str, current_user: User, limit: int, db: AsyncSession
) -> List[UserSearchResponse]:
    """
    Searches registered users by username, email, or phone number substring for autocompletion.
    Excludes the current user from search results.

    Args:
        query (str): Search query string.
        current_user (User): Current user to exclude.
        limit (int): Maximum items to return.
        db (AsyncSession): Database session.

    Returns:
        List[UserSearchResponse]: List of matching user items.
    """
    if not query or len(query.strip()) == 0:
        return []

    search_pattern = f"%{query.strip()}%"
    stmt = (
        select(User)
        .where(
            User.id != current_user.id,
            or_(
                User.username.ilike(search_pattern),
                User.email.ilike(search_pattern),
                User.phone_number.ilike(search_pattern),
                User.full_name.ilike(search_pattern),
            ),
        )
        .limit(limit)
    )
    result = await db.execute(stmt)
    users = result.scalars().all()
    return [UserSearchResponse.model_validate(u) for u in users]
