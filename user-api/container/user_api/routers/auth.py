from fastapi import APIRouter, Response, status
from pydantic import UUID4

from user_api.internal import auth
from user_api.routers import api_models
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


@router.put("/users/{username}")
async def user_update(
    username: str,
    user_update_request: api_models.UserUpdateRequest,
) -> Response:
    """Change a authenticated user's password."""
    with sanitize_excs():
        await auth.change_password(username, user_update_request.password)
    return success


@router.delete("/users/{username}")
async def user_delete(username: str) -> Response:
    """Delete a user account."""
    with sanitize_excs():
        await auth.delete(username)
    return success


@router.post("/users/{username}/login")
async def user_login(
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


@router.delete("/tokens/{client_token}")
async def token_delete(client_token: UUID4) -> Response:
    """Log the currently authenticated user out."""
    with sanitize_excs():
        await auth.logout_by_client_token(client_token)
    return success
