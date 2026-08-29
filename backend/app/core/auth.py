from jose import JWTError
from fastapi import HTTPException, Depends, status
from app.core.dependencies import verify_token, oauth2_scheme
from app.database.session import asyncSession
from app.database.models.user import User


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    FastAPI dependency to validate JWT bearer token and return authenticated User ORM instance.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        async with asyncSession() as db:
            user = await verify_token(token, db)
            return user
    except Exception:
        raise credentials_exception