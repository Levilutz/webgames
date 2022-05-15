from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import UUID4

from user_api.daos import User
from user_api.internal import auth
from user_api.routers import api_models, dependencies
from user_api.routers.utils import sanitize_excs


router = APIRouter()


@router.post("/register")
async def register(
    register_request: api_models.AuthRequest,
) -> api_models.SuccessResponse:
    """Register a new user."""
    with sanitize_excs():
        await auth.register(
            username=register_request.username,
            password=register_request.password,
        )
    return api_models.success


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> api_models.AuthLoginResponse:
    """Log a user in."""
    with sanitize_excs():
        session = await auth.login(
            username=form_data.username,
            password=form_data.password,
        )
    return api_models.AuthLoginResponse(access_token=session.client_token.hex)


@router.post("/login_json")
async def login_json(
    login_request: api_models.AuthRequest,
) -> api_models.AuthLoginResponseSimple:
    """Log a user in, just using json (non-OAuth2-compliant endpoint)."""
    with sanitize_excs():
        session = await auth.login(
            # Keep explicit (no **) to avoid leaking extra params from request
            username=login_request.username,
            password=login_request.password,
        )
    return api_models.AuthLoginResponseSimple(client_token=session.client_token.hex)


@router.post("/logout")
async def logout(
    token: UUID4 = Depends(dependencies.get_token),
) -> api_models.SuccessResponse:
    """Log the currently authenticated user out."""
    with sanitize_excs():
        await auth.logout_by_client_token(token)
    return api_models.success


@router.post("/change_password")
async def change_password(
    change_password_request: api_models.ChangePasswordRequest,
    user: User = Depends(dependencies.get_user),
) -> api_models.SuccessResponse:
    """Change a authenticated user's password."""
    with sanitize_excs():
        await auth.change_password(user.user_id, change_password_request.new_password)
    return api_models.success
