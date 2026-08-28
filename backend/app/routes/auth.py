from fastapi import APIRouter

from app.services.signup_services import create_user
from app.database.schemas.user import UserCreate,UserResponse

router = APIRouter(prefix="/auth",tags=["Authentication"])

@router.post("/signup", response_model=UserResponse,status_code=201)
async def signup(user_data: UserCreate):
    return await create_user(user_data=user_data)

