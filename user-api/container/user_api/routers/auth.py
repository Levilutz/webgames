from fastapi import APIRouter, Depends, Response, status
from pydantic import UUID4

from user_api.daos import User
from user_api.internal import auth
from user_api.routers import api_models, dependencies
from user_api.routers.utils import sanitize_excs


router = APIRouter()

success = Response(status_code=status.HTTP_200_OK)


@router.post("/users/{username}")
async def user_create(
    username: str,
    user_create_request: api_models.UserCreateRequest,
) -> Response:
    """Register a new user."""
    with sanitize_excs():
        await auth.register(
            username=username,
            password=user_create_request.password,
        )
    return success


@router.delete("/users/{username}")
async def user_delete(username: str) -> Response:
    """Delete a user account."""
    with sanitize_excs():
        await auth.delete(username)
    return success


@router.post("/users/{username}/login")
async def login(
    username: str,
    user_login_request: api_models.UserLoginRequest,
) -> api_models.AuthLoginResponse:
    """Log a user in, just using json (non-OAuth2-compliant endpoint)."""
    with sanitize_excs():
        session = await auth.login(
            username=username,
            password=user_login_request.password,
        )
    return api_models.AuthLoginResponse(client_token=session.client_token.hex)


@router.post("/logout")
async def logout(
    token: UUID4 = Depends(dependencies.get_token),
) -> Response:
    """Log the currently authenticated user out."""
    with sanitize_excs():
        await auth.logout_by_client_token(token)
    return success


@router.post("/change_password")
async def change_password(
    change_password_request: api_models.ChangePasswordRequest,
    user: User = Depends(dependencies.get_user),
) -> Response:
    """Change a authenticated user's password."""
    with sanitize_excs():
        await auth.change_password(user.user_id, change_password_request.new_password)
    return success
