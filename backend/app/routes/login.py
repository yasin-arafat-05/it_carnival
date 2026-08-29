from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.database.schemas.token import Token
from app.services.login_services import login_for_access_token

router = APIRouter(tags=["Authentication"])


@router.post(
    "/token",
    response_model=Token,
    summary="OAuth2 Form Login Token",
    description="OAuth2 Form Data endpoint for Swagger UI and form login requests.",
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 Form token generation endpoint.
    """
    result = await login_for_access_token(form_data)
    return {"access_token": result, "token_type": "bearer"}
