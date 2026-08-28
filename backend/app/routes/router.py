from fastapi import APIRouter
from app.routes.auth import router as auth_router
from app.routes.login import router as login_router
from app.routes.sse import router as sse_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(login_router)
api_router.include_router(sse_router)

