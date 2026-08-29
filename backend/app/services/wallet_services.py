import uuid
from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, or_, and_, desc, text, func
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.locks import LOCK_MANAGER
from app.database.models.user import User
from app.database.models.account import Account
from app.database.models.transaction import Transaction
from app.database.models.ledger import LedgerEntry
from app.database.models.notification import Notification
from app.database.schemas.account import AccountResponse, WalletDashboardResponse
from app.database.schemas.transaction import SendMoneyRequest, TransactionResponse
from app.database.schemas.ledger import LedgerEntryResponse


def build_transaction_response(tx: Transaction) -> TransactionResponse:
    """
    Helper function to construct TransactionResponse populating sender_username and receiver_username.

    Args:
        tx (Transaction): Transaction ORM instance.

    Returns:
        TransactionResponse: Schema populated with usernames.
    """
    res = TransactionResponse.model_validate(tx)
    if getattr(tx, "sender_account", None) and getattr(tx.sender_account, "user", None):
        res.sender_username = tx.sender_account.user.username
    if getattr(tx, "receiver_account", None) and getattr(tx.receiver_account, "user", None):
        res.receiver_username = tx.receiver_account.user.username
    return res


async def get_account_by_user_id(user_id: uuid.UUID, db: AsyncSession) -> Account:
    """
    Helper function to fetch an active Account by user ID.

    Args:
        user_id (UUID): Owning user ID.
        db (AsyncSession): Database session.

    Returns:
        Account: Account ORM instance.

    Raises:
        HTTPException: 404 Not Found if account missing or inactive.
    """
    result = await db.execute(select(Account).where(Account.user_id == user_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet account not found for current user.",
        )
    return account


async def get_wallet_dashboard(user: User, db: AsyncSession) -> WalletDashboardResponse:
    """
    Fetches account balances and top recent transactions for the user wallet dashboard.

    Args:
        user (User): Current authenticated user.
        db (AsyncSession): Database session.

    Returns:
        WalletDashboardResponse: Dashboard response object.
    """
    account = await get_account_by_user_id(user.id, db)

    # Query recent 10 transactions eagerly loading account users
    tx_query = (
        select(Transaction)
        .options(
            joinedload(Transaction.sender_account).joinedload(Account.user),
            joinedload(Transaction.receiver_account).joinedload(Account.user),
        )
        .where(
            or_(
                Transaction.sender_account_id == account.id,
                Transaction.receiver_account_id == account.id,
            )
        )
        .order_by(desc(Transaction.created_at))
        .limit(10)
    )
    tx_result = await db.execute(tx_query)
    recent_txs = tx_result.scalars().all()

    tx_responses = []
    for tx in recent_txs:
        res = build_transaction_response(tx)
        tx_responses.append(res.model_dump(mode="json"))

    return WalletDashboardResponse(
        account=AccountResponse.model_validate(account),
        recent_transactions=tx_responses,
    )


async def execute_transfer(
    sender_user: User, transfer_data: SendMoneyRequest, db: AsyncSession
) -> TransactionResponse:
    """
    Executes an atomic money movement transfer between accounts.
    Uses Python's `threading` module (threading.RLock via LOCK_MANAGER) to guarantee in-process
    thread mutual exclusion across critical sections, alongside database row-level locking.

    Args:
        sender_user (User): Authenticated sender user.
        transfer_data (SendMoneyRequest): Transfer payload details.
        db (AsyncSession): Database session.

    Returns:
        TransactionResponse: Completed transaction details.

    Raises:
        HTTPException: 400 Bad Request, 404 Not Found, or 403 Forbidden.
    """
    if sender_user.role == "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin users are restricted from executing financial transactions.",
        )

    # 1. Threading Lock Key Selection
    thread_lock_key = f"transfer_user_{sender_user.id}"
    if transfer_data.idempotency_key:
        thread_lock_key = f"transfer_key_{transfer_data.idempotency_key}"

    thread_lock = LOCK_MANAGER.get_lock(thread_lock_key)

    # 2. Enter Critical Section using Python threading.RLock
    with thread_lock:
        # Idempotency Check (under thread lock)
        if transfer_data.idempotency_key:
            existing_tx = await db.execute(
                select(Transaction)
                .options(
                    joinedload(Transaction.sender_account).joinedload(Account.user),
                    joinedload(Transaction.receiver_account).joinedload(Account.user),
                )
                .where(Transaction.idempotency_key == transfer_data.idempotency_key)
            )
            found_tx = existing_tx.scalar_one_or_none()
            if found_tx:
                return build_transaction_response(found_tx)

        # Optional PostgreSQL Transaction Advisory Lock fallback
        lock_int = int(uuid.uuid5(uuid.NAMESPACE_DNS, thread_lock_key).int % 2147483647)
        try:
            await db.execute(text("SELECT pg_advisory_xact_lock(:lock_id)"), {"lock_id": lock_int})
        except Exception:
            pass

        # Resolve Receiver User
        rx_identifier = transfer_data.receiver_identifier.strip()
        rx_conditions = [
            User.username == rx_identifier,
            User.email == rx_identifier,
            User.phone_number == rx_identifier,
        ]
        try:
            rx_uuid = uuid.UUID(rx_identifier)
            rx_conditions.append(User.id == rx_uuid)
        except ValueError:
            pass

        receiver_query = select(User).where(or_(*rx_conditions))
        receiver_res = await db.execute(receiver_query)
        receiver_user = receiver_res.scalar_one_or_none()

        if not receiver_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Receiver user '{transfer_data.receiver_identifier}' not found.",
            )

        # Self-transfer check
        if receiver_user.id == sender_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Self-transfer is not allowed.",
            )

        # Fetch Account IDs
        sender_account_res = await db.execute(select(Account.id, Account.status).where(Account.user_id == sender_user.id))
        sender_row = sender_account_res.first()
        if not sender_row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sender wallet account not found.")
        if sender_row.status != "ACTIVE":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sender account is suspended or inactive.")

        receiver_account_res = await db.execute(select(Account.id, Account.status).where(Account.user_id == receiver_user.id))
        receiver_row = receiver_account_res.first()
        if not receiver_row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver wallet account not found.")
        if receiver_row.status != "ACTIVE":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Receiver account is currently suspended.")

        sender_account_id = sender_row.id
        receiver_account_id = receiver_row.id

        # Deterministic Row-Level Locking (FOR UPDATE)
        locked_account_ids = sorted([sender_account_id, receiver_account_id])
        lock_query = (
            select(Account)
            .where(Account.id.in_(locked_account_ids))
            .with_for_update()
        )
        locked_results = await db.execute(lock_query)
        locked_accounts_map = {acc.id: acc for acc in locked_results.scalars().all()}

        locked_sender = locked_accounts_map[sender_account_id]
        locked_receiver = locked_accounts_map[receiver_account_id]

        # Check Balance against locked state
        transfer_amount = Decimal(str(transfer_data.amount))

        # Single transaction limit check (Max BDT 20,000)
        SINGLE_TX_MAX = Decimal("20000.00")
        if transfer_amount > SINGLE_TX_MAX:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Single transaction amount cannot exceed BDT 20,000.00.",
            )

        # Daily transfer limit check (Max BDT 50,000 per user per day)
        DAILY_LIMIT_MAX = Decimal("50000.00")
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_sent_stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.sender_account_id == locked_sender.id,
            Transaction.status == "COMPLETED",
            Transaction.created_at >= today_start,
        )
        today_sent_res = await db.execute(today_sent_stmt)
        today_sent_amount = today_sent_res.scalar() or Decimal("0.00")

        if today_sent_amount + transfer_amount > DAILY_LIMIT_MAX:
            remaining_limit = max(Decimal("0.00"), DAILY_LIMIT_MAX - today_sent_amount)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Daily transfer limit of BDT 50,000.00 exceeded. Remaining limit for today: BDT {remaining_limit:,.2f}.",
            )

        if locked_sender.available_balance < transfer_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance. Available: BDT {locked_sender.available_balance:,.2f}, Requested: BDT {transfer_amount:,.2f}.",
            )

        try:
            # Execute Debits and Credits
            locked_sender.balance -= transfer_amount
            locked_sender.available_balance -= transfer_amount

            locked_receiver.balance += transfer_amount
            locked_receiver.available_balance += transfer_amount

            # Create Transaction Record
            now_str = datetime.utcnow().strftime("%Y%m%d")
            tx_ref = f"TX-{now_str}-{uuid.uuid4().hex[:6].upper()}"
            transaction = Transaction(
                reference_id=tx_ref,
                sender_account_id=locked_sender.id,
                receiver_account_id=locked_receiver.id,
                amount=transfer_amount,
                currency="BDT",
                transaction_type="TRANSFER",
                status="COMPLETED",
                idempotency_key=transfer_data.idempotency_key,
                note=transfer_data.note,
            )
            db.add(transaction)
            await db.flush()

            # Create Double-Entry Ledger Entries
            sender_ledger = LedgerEntry(
                transaction_id=transaction.id,
                account_id=locked_sender.id,
                entry_type="DEBIT",
                amount=transfer_amount,
                balance_after=locked_sender.balance,
            )
            receiver_ledger = LedgerEntry(
                transaction_id=transaction.id,
                account_id=locked_receiver.id,
                entry_type="CREDIT",
                amount=transfer_amount,
                balance_after=locked_receiver.balance,
            )
            db.add_all([sender_ledger, receiver_ledger])

            # Dispatch Notifications
            sender_notif = Notification(
                user_id=sender_user.id,
                title="Transfer Sent",
                message=f"You successfully sent BDT {transfer_amount:,.2f} to {receiver_user.username}.",
                notification_type="TRANSFER_SENT",
                reference_id=tx_ref,
            )
            receiver_notif = Notification(
                user_id=receiver_user.id,
                title="Money Received",
                message=f"You received BDT {transfer_amount:,.2f} from {sender_user.username}.",
                notification_type="TRANSFER_RECEIVED",
                reference_id=tx_ref,
            )
            db.add_all([sender_notif, receiver_notif])

            # Commit Transaction
            await db.commit()
            await db.refresh(transaction)

            res = TransactionResponse.model_validate(transaction)
            res.sender_username = sender_user.username
            res.receiver_username = receiver_user.username
            return res

        except HTTPException:
            await db.rollback()
            raise

        except Exception as e:
            await db.rollback()
            print(f"Error during money transfer execution: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transfer execution failed: {str(e)}",
            )


async def get_transaction_history(
    user: User, page: int, limit: int, db: AsyncSession
) -> List[TransactionResponse]:
    """
    Retrieves paginated transaction history for the user with sender and receiver usernames populated.

    Args:
        user (User): Authenticated user.
        page (int): Page number (1-indexed).
        limit (int): Items per page.
        db (AsyncSession): Database session.

    Returns:
        List[TransactionResponse]: List of transactions.
    """
    account = await get_account_by_user_id(user.id, db)
    offset = (page - 1) * limit

    query = (
        select(Transaction)
        .options(
            joinedload(Transaction.sender_account).joinedload(Account.user),
            joinedload(Transaction.receiver_account).joinedload(Account.user),
        )
        .where(
            or_(
                Transaction.sender_account_id == account.id,
                Transaction.receiver_account_id == account.id,
            )
        )
        .order_by(desc(Transaction.created_at))
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    transactions = result.scalars().all()
    return [build_transaction_response(tx) for tx in transactions]


async def get_transaction_by_reference(
    reference_id: str, user: User, db: AsyncSession
) -> TransactionResponse:
    """
    Fetches detailed information for a single transaction by reference ID with usernames populated.

    Args:
        reference_id (str): Reference string (e.g. TX-20260829-82931).
        user (User): Authenticated user.
        db (AsyncSession): Database session.

    Returns:
        TransactionResponse: Transaction item.

    Raises:
        HTTPException: 404 Not Found if missing or unauthorized.
    """
    account = await get_account_by_user_id(user.id, db)
    query = (
        select(Transaction)
        .options(
            joinedload(Transaction.sender_account).joinedload(Account.user),
            joinedload(Transaction.receiver_account).joinedload(Account.user),
        )
        .where(
            and_(
                Transaction.reference_id == reference_id,
                or_(
                    Transaction.sender_account_id == account.id,
                    Transaction.receiver_account_id == account.id,
                ),
            )
        )
    )
    result = await db.execute(query)
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction record not found or access denied.",
        )
    return build_transaction_response(tx)


async def get_ledger_entries(
    user: User, page: int, limit: int, db: AsyncSession
) -> List[LedgerEntryResponse]:
    """
    Retrieves double-entry ledger audit logs for the user's account.

    Args:
        user (User): Authenticated user.
        page (int): Page number.
        limit (int): Items per page.
        db (AsyncSession): Database session.

    Returns:
        List[LedgerEntryResponse]: List of ledger entry snapshots.
    """
    account = await get_account_by_user_id(user.id, db)
    offset = (page - 1) * limit

    query = (
        select(LedgerEntry)
        .where(LedgerEntry.account_id == account.id)
        .order_by(desc(LedgerEntry.created_at))
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    entries = result.scalars().all()
    return [LedgerEntryResponse.model_validate(e) for e in entries]
