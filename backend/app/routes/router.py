from fastapi import APIRouter
from app.routes.auth import router as auth_router
from app.routes.login import router as login_router
from app.routes.wallet import router as wallet_router
from app.routes.money_request import router as money_request_router
from app.routes.user import router as user_router
from app.routes.notification import router as notification_router
from app.routes.health import router as health_router
from app.routes.sse import router as sse_router
from app.routes.dispute import router as dispute_router
from app.routes.admin import router as admin_router

api_router = APIRouter()

# Register Authentication & Login endpoints
api_router.include_router(auth_router)
api_router.include_router(login_router)

# Register Digital Wallet, Money Movement & Dispute Reversal endpoints
api_router.include_router(wallet_router)
api_router.include_router(money_request_router)
api_router.include_router(dispute_router)

# Register Administrative Panel & Audit endpoints
api_router.include_router(admin_router)

# Register User Profile & Search endpoints
api_router.include_router(user_router)

# Register Notification endpoints
api_router.include_router(notification_router)

# Register System Health & AI Chat SSE endpoints
api_router.include_router(health_router)
api_router.include_router(sse_router)
