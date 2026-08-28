from jose import JWTError
from app.core.config import CONFIG
from app.database.session import asyncSession
from app.core.security import verify_token
from fastapi import HTTPException,Depends,status
from app.database.schemas.user import TokenResponse
from fastapi.security import OAuth2PasswordBearer

#oauth2 scheme:
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


#get the current user: when a user authorized:
async def get_current_user(token: str = Depends(oauth2_scheme)):
    print("token: in get current user: "+ token)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        async with asyncSession() as db:
            user = await verify_token(token,db)
        output = TokenResponse.model_validate(user)
        print(output)
        return user
    except JWTError:
        raise credentials_exception