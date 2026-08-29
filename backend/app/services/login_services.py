from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.models.user import User
from app.database.schemas.token import Token
from app.database.schemas.user import UserResponse, TokenResponse, UserLogin
from app.database.session import asyncSession
from app.core.security import authenticate_user, create_access_token


async def login_user(login_data: UserLogin) -> TokenResponse:
    """
    Authenticates a user via credential identifier (Email, Username, or Phone Number) and password,
    issuing a signed JWT access token.

    Args:
        login_data (UserLogin): User login credentials.

    Returns:
        TokenResponse: Access token and public user profile response.

    Raises:
        HTTPException: 401 Unauthorized if credentials are invalid or account suspended.
    """
    async with asyncSession() as db:
        user = await authenticate_user(login_data.identifier, login_data.password, db)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username/email/phone or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user.account_status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account access restricted: Account status is '{user.account_status}'.",
            )

        # Eagerly load user with account relationship to populate UserResponse cleanly
        query = select(User).where(User.id == user.id).options(selectinload(User.account))
        res = await db.execute(query)
        full_user = res.scalar_one()

    access_token = create_access_token(
        data={"id": str(full_user.id), "email": full_user.email, "username": full_user.username}
    )
    user_response = UserResponse.model_validate(full_user)
    return TokenResponse(access_token=access_token, token_type="bearer", user=user_response)


async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token endpoint handler for Swagger UI and form-data logins.

    Args:
        form_data (OAuth2PasswordRequestForm): Form containing username (identifier) and password.

    Returns:
        str: JWT access token.
    """
    async with asyncSession() as db:
        user = await authenticate_user(form_data.username, form_data.password, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email/phone or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.account_status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account access restricted: Account status is '{user.account_status}'.",
        )

    access_token = create_access_token(
        data={"id": str(user.id), "email": user.email, "username": user.username}
    )
    return access_token