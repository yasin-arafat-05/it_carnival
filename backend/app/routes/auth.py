from fastapi import APIRouter, status
from app.services.signup_services import create_user
from app.services.login_services import login_user
from app.database.schemas.user import UserCreate, UserResponse, UserLogin, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User & Funding",
    description="Registers a new user account with strict password validation and automatically credits BDT 100,000 initial funding.",
)
async def signup(user_data: UserCreate) -> UserResponse:
    """
    Registers a new user and provisions a digital wallet account with BDT 100,000 initial balance.
    """
    return await create_user(user_data=user_data)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login (JSON Payload)",
    description="Authenticates user using Email, Username, or Phone Number and returns a JWT access token.",
)
async def login_json(login_data: UserLogin) -> TokenResponse:
    """
    Authenticates user and returns JWT bearer token along with user profile.
    """
    return await login_user(login_data=login_data)
