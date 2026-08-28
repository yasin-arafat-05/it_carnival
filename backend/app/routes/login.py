from fastapi import APIRouter, Depends
from app.database.schemas.token import Token
from fastapi.security import OAuth2PasswordRequestForm
from app.services.login_services import login_for_access_token

router = APIRouter(tags=['login'])

# Token generation endpoint/login endpoint
@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),):
    result = await login_for_access_token(form_data)
    return {"access_token": result, "token_type": "bearer"}
