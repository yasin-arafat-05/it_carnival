from sqlalchemy import select
from fastapi import HTTPException, status
from app.database.models.user import User
from app.database.session import asyncSession
from app.core.security import get_password_hash
from app.database.schemas.user import UserCreate,UserResponse


async def create_user(user_data: UserCreate):
   curret_user_data = user_data.model_dump(exclude={"password"})
   curret_user_data['password_hash'] = get_password_hash(user_data.password)
   try:
    async with asyncSession() as db:
        res = await db.execute(select(User).where(User.email==user_data.email))
        fetch_user_data = res.scalar_one_or_none()
        # check email:
        if fetch_user_data:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists.")
        

        res = await db.execute(select(User).where(User.phone_number==user_data.phone_number))
        fetch_user_data = res.scalar_one_or_none()
        # check phone number:
        if fetch_user_data:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone Number already exists.")
        
        # let's processed:
        new_user = User(**curret_user_data)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return UserResponse.model_validate(new_user)
   except HTTPException:
       raise 
   
   except Exception as e:
        await db.rollback()
        print(f"error while signup: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    

