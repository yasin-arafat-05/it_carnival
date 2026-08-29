from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.session import asyncSession
from app.database.models.user import User
from app.database.schemas.user import UserResponse, UserSearchResponse
from app.services.user_services import get_current_user_profile, search_users

router = APIRouter(prefix="/users", tags=["User Profile & Search"])


async def get_db():
    async with asyncSession() as session:
        yield session


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Authenticated User Profile & Wallet Balance",
    description="Fetches profile information of current user along with their digital wallet account balance and status.",
)
async def me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Get current user profile & wallet balance endpoint.
    """
    return await get_current_user_profile(user=current_user, db=db)


@router.get(
    "/search",
    response_model=List[UserSearchResponse],
    summary="Search Users for Transfers/Requests",
    description="Search registered users by username, email, or phone number substring.",
)
async def search(
    query: str = Query(..., min_length=1, description="Search term (username, email, or phone)"),
    limit: int = Query(10, ge=1, le=50, description="Max search results"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[UserSearchResponse]:
    """
    User search autocompletion endpoint.
    """
    return await search_users(query=query, current_user=current_user, limit=limit, db=db)
