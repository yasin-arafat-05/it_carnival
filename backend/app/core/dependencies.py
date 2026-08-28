import jwt 
from sqlalchemy import select 
from pwdlib import PasswordHash
from app.core.config import CONFIG
from datetime import datetime,timedelta
from fastapi import HTTPException,status
from app.database.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

password_hash = PasswordHash.recommended()

# hash encoding 
def get_password_hash(password):
    return password_hash.hash(password)

# hash decoding
def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


# check the token validity:
async def verify_token(token: str, db: AsyncSession):
    try:
        payload = jwt.decode(token,CONFIG.SECRET_KEY, algorithms=CONFIG.ALGORITHM)
        print(f"Decoded payload: {payload}")
        user_id = payload.get("id")
        if user_id:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                return user
            else:
                print(f"User with id {user_id} not found in the database.")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: User not found.",
                    headers={"WWW-Authenticate": "Bearer"}
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: Missing user ID.",
                headers={"WWW-Authenticate": "Bearer"}
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    


#authenticate user
async def authenticate_user(username: str, password: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == username))
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


# Function to create access token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=180)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode,CONFIG.SECRET_KEY, algorithm=CONFIG.ALGORITHM)
    return encoded_jwt
