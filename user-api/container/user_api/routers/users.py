from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import UUID4

from user_api.internal import users
from user_api.routers import api_models, dependencies
from user_api.routers.utils import sanitize_excs


router = APIRouter()


@router.post("/register")
async def register(
    register_request: api_models.RegisterRequest,
) -> api_models.SuccessResponse:
    """Register a new user."""
    with sanitize_excs():
        await users.register(
            username=register_request.username,
            password=register_request.password,
        )
    return api_models.success


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> api_models.AuthLoginResponse:
    """Log a user in."""
    session = await users.login(
        username=form_data.username,
        password=form_data.password,
    )
    return api_models.AuthLoginResponse(access_token=session.client_token.hex)


@router.post("/logout")
async def logout(
    token: UUID4 = Depends(dependencies.get_token),
) -> api_models.SuccessResponse:
    """Log the currently authenticated user out."""
    await users.logout_by_client_token(token)
    return api_models.success
