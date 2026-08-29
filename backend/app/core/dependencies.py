import jwt
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from pwdlib import PasswordHash
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import CONFIG
from app.database.models.user import User
from app.database.session import asyncSession

# Initialize PasswordHash using Argon2id recommended standard
password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def get_password_hash(password: str) -> str:
    """
    Hashes a plain text password using Argon2id.

    Args:
        password (str): Plain text password string.

    Returns:
        str: Secure Argon2id hashed password string.
    """
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against an Argon2id hashed password.

    Args:
        plain_password (str): Plain text candidate password.
        hashed_password (str): Stored Argon2id hash.

    Returns:
        bool: True if password matches hash, False otherwise.
    """
    return password_hash.verify(plain_password, hashed_password)


async def verify_token(token: str, db: AsyncSession) -> User:
    """
    Decodes and verifies a JWT access token, looking up the authenticated user along with their account.

    Args:
        token (str): Bearer JWT token string.
        db (AsyncSession): SQLAlchemy async database session.

    Returns:
        User: Authenticated User ORM instance.

    Raises:
        HTTPException: 401 Unauthorized if token is expired, invalid, or user non-existent.
    """
    try:
        payload = jwt.decode(token, CONFIG.SECRET_KEY, algorithms=[CONFIG.ALGORITHM])
        user_id: Optional[str] = payload.get("id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token: missing user identifier.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        result = await db.execute(
            select(User).where(User.id == user_id).options(selectinload(User.account))
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed: User account not found.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if user.account_status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account access restricted: Account status is '{user.account_status}'.",
            )
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> User:
    """
    FastAPI Dependency to retrieve the currently authenticated user from Bearer Token.

    Args:
        token (str): JWT Bearer token extracted from Authorization header.

    Returns:
        User: Authenticated active user object.
    """
    async with asyncSession() as db:
        return await verify_token(token, db)


async def require_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    FastAPI Dependency enforcing ADMIN role authorization for administrative endpoints.

    Args:
        current_user (User): Current authenticated user.

    Returns:
        User: Admin user instance.

    Raises:
        HTTPException: 403 Forbidden if current user is not an administrator.
    """
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted: Administrative privileges required.",
        )
    return current_user


async def authenticate_user(
    identifier: str, password: str, db: AsyncSession
) -> Optional[User]:
    """
    Authenticates a user via Email, Username, or Phone Number and verifies password.

    Args:
        identifier (str): User's email, username, or phone number.
        password (str): User's plain text password candidate.
        db (AsyncSession): SQLAlchemy async session.

    Returns:
        Optional[User]: User ORM instance if authenticated successfully, None otherwise.
    """
    result = await db.execute(
        select(User)
        .where(
            or_(
                User.email == identifier,
                User.username == identifier,
                User.phone_number == identifier,
            )
        )
        .options(selectinload(User.account))
    )
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Encodes data payload into a signed JWT access token.

    Args:
        data (dict): Payload claims to encode (e.g. {"id": user_id, "email": email}).
        expires_delta (Optional[timedelta]): Token expiration duration.

    Returns:
        str: Encoded JWT token string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, CONFIG.SECRET_KEY, algorithm=CONFIG.ALGORITHM)
    return encoded_jwt
