import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.database.models.user import User
from app.database.models.account import Account
from app.database.models.transaction import Transaction
from app.database.models.ledger import LedgerEntry
from app.database.models.notification import Notification
from app.database.session import asyncSession
from app.core.security import get_password_hash
from app.database.schemas.user import UserCreate, UserResponse

INITIAL_BALANCE = Decimal("100000.00")


async def create_user(user_data: UserCreate) -> UserResponse:
    """
    Registers a new user account, enforces field uniqueness, hashes password,
    creates a digital wallet account, and automatically executes initial BDT 100,000 funding
    with complete double-entry ledger entries and notification.

    Args:
        user_data (UserCreate): Validated user registration request payload.

    Returns:
        UserResponse: Created user profile response schema.

    Raises:
        HTTPException: 409 Conflict if email, username, or phone number already exists.
        HTTPException: 400 Bad Request if database transaction execution fails.
    """
    async with asyncSession() as db:
        try:
            # Check for existing email, username, or phone number
            query = select(User).where(
                or_(
                    User.email == user_data.email,
                    User.username == user_data.username,
                    User.phone_number == user_data.phone_number,
                )
            )
            result = await db.execute(query)
            existing_user = result.scalar_one_or_none()

            if existing_user:
                if existing_user.email == user_data.email:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="An account with this email address already exists.",
                    )
                if existing_user.username == user_data.username:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="This username is already taken.",
                    )
                if existing_user.phone_number == user_data.phone_number:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="An account with this phone number already exists.",
                    )

            # Hash the user's password securely with Argon2id
            hashed_pwd = get_password_hash(user_data.password)

            # 1. Create User instance (Default role='USER')
            new_user = User(
                full_name=user_data.full_name,
                username=user_data.username,
                phone_number=user_data.phone_number,
                email=user_data.email,
                password_hash=hashed_pwd,
                role="USER",
                account_status="ACTIVE",
            )
            db.add(new_user)
            await db.flush()  # Flush to generate new_user.id

            # 2. Automatically Create Digital Wallet Account
            account_no = f"ACC-{uuid.uuid4().hex[:8].upper()}"
            new_account = Account(
                user_id=new_user.id,
                account_number=account_no,
                balance=INITIAL_BALANCE,
                available_balance=INITIAL_BALANCE,
                currency="BDT",
                status="ACTIVE",
            )
            db.add(new_account)
            await db.flush()  # Flush to generate new_account.id

            # 3. Record Initial Credit Transaction
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
            await db.flush()  # Flush to generate initial_tx.id

            # 4. Record Double-Entry Ledger Entry
            ledger_entry = LedgerEntry(
                transaction_id=initial_tx.id,
                account_id=new_account.id,
                entry_type="CREDIT",
                amount=INITIAL_BALANCE,
                balance_after=INITIAL_BALANCE,
            )
            db.add(ledger_entry)

            # 5. Create Welcome Notification
            welcome_notification = Notification(
                user_id=new_user.id,
                title="Account Funded",
                message=f"Welcome to your Digital Wallet! Your account has been credited with BDT {INITIAL_BALANCE:,.2f} initial balance.",
                notification_type="INITIAL_CREDIT",
                reference_id=tx_ref,
            )
            db.add(welcome_notification)

            # Commit atomic transaction
            await db.commit()

            # Eagerly load user with account relationship to prevent MissingGreenlet error
            user_query = select(User).where(User.id == new_user.id).options(selectinload(User.account))
            fetch_res = await db.execute(user_query)
            registered_user = fetch_res.scalar_one()

            return UserResponse.model_validate(registered_user)

        except HTTPException:
            await db.rollback()
            raise

        except Exception as e:
            await db.rollback()
            print(f"Error during user registration: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User registration failed: {str(e)}",
            )
