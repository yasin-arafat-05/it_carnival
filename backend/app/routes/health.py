from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import asyncSession
from app.services.system_services import check_system_health

router = APIRouter(tags=["System Observability"])


async def get_db():
    async with asyncSession() as session:
        yield session


@router.get(
    "/health",
    summary="System Health Status",
    description="Returns database connectivity and operational status for system observability.",
)
async def health(db: AsyncSession = Depends(get_db)) -> dict:
    """
    System status observability endpoint.
    """
    return await check_system_health(db=db)
