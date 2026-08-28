from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.database.schemas.token import Token
from app.database.session import asyncSession
from app.core.security import authenticate_user, create_access_token


async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    async with asyncSession() as db:
        user = await authenticate_user(form_data.username, form_data.password, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"id": str(user.id), "email": user.email})
    return access_token
    