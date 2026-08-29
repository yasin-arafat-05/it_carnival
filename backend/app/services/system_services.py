from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def check_system_health(db: AsyncSession) -> dict:
    """
    Checks database connection and system operational health.

    Args:
        db (AsyncSession): Database session.

    Returns:
        dict: Health status report.
    """
    try:
        await db.execute(text("SELECT 1"))
        db_status = "Connected"
    except Exception as e:
        db_status = f"Disconnected ({str(e)})"

    return {
        "status": "Healthy" if db_status == "Connected" else "Degraded",
        "database": db_status,
        "service": "EduManage API",
    }
