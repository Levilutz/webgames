from fastapi import APIRouter, Response, status
from pydantic import UUID4

from user_api.config import EMAIL_ENABLED
from user_api.exceptions import NotFoundError
from user_api.internal import auth
from user_api.routers import api_models
from user_api.routers.utils import sanitize_excs


router = APIRouter()

success = Response(status_code=status.HTTP_200_OK)


@router.post("/pre_users")
async def pre_user_create(
    pre_user_create_request: api_models.PreUserCreateRequest,
) -> api_models.PreUserCreateResponse:
    """Create a pre-user (unverified email address)."""
    with sanitize_excs():
        pre_user = await auth.preregister(
            email_address=pre_user_create_request.email_address,
        )
        # If email disabled, pass verify code right back to user
        verify_code = None if EMAIL_ENABLED else pre_user.verify_code
        resp = api_models.PreUserCreateResponse(verify_code=verify_code)
    return resp


@router.post("/pre_users/verify")
async def pre_user_verify(
    pre_user_verify_request: api_models.PreUserVerifyRequest,
) -> Response:
    """Verify a pre-user verification code."""
    with sanitize_excs():
        # Raises exc if verification fails
        await auth.preregister_verify(
            email_address=pre_user_verify_request.email_address,
            verify_code=pre_user_verify_request.verify_code,
        )
    return success


@router.post("/users")
async def user_create(
    user_create_request: api_models.UserCreateRequest,
) -> Response:
    """Register a new user."""
    with sanitize_excs():
        # Don't expand with ** to avoid leaking request fields
        await auth.register(
            email_address=user_create_request.email_address,
            password=user_create_request.password,
            first_name=user_create_request.first_name,
            last_name=user_create_request.last_name,
            verify_code=user_create_request.verify_code,
        )
    return success


@router.put("/users")
async def user_update(
    user_update_request: api_models.UserUpdateRequest,
) -> Response:
    """Change a user's information."""
    with sanitize_excs():
        if user_update_request.password is not None:
            # Don't expand with ** to avoid leaking request fields
            await auth.change_password(
                email_address=user_update_request.email_address,
                new_password=user_update_request.password,
            )
        if (
            user_update_request.first_name is not None
            or user_update_request.last_name is not None
        ):
            # Don't expand with ** to avoid leaking request fields
            await auth.change_name(
                email_address=user_update_request.email_address,
                first_name=user_update_request.first_name,
                last_name=user_update_request.last_name,
            )
    return success


@router.delete("/users")
async def user_delete(user_delete_request: api_models.UserDeleteRequest) -> Response:
    """Delete a user account."""
    with sanitize_excs():
        await auth.delete(email_address=user_delete_request.email_address)
    return success


# This is essentially the token create endpoint, it just has specific requirements
@router.post("/users/login")
async def user_login(
    user_login_request: api_models.UserLoginRequest,
) -> api_models.UserLoginResponse:
    """Log a user in."""
    with sanitize_excs():
        session = await auth.login(
            email_address=user_login_request.email_address,
            password=user_login_request.password,
        )
        resp = api_models.UserLoginResponse(client_token=session.client_token.hex)
    return resp


@router.get("/tokens/{client_token}")
async def token_get(client_token: UUID4) -> api_models.TokenGetResponse:
    """Get data for a given token."""
    with sanitize_excs():
        user = await auth.find_by_token(client_token)
        if user is None:
            raise NotFoundError("Failed to find token")
        resp = api_models.TokenGetResponse(email_address=user.email_address)
    return resp


@router.delete("/tokens/{client_token}")
async def token_delete(client_token: UUID4) -> Response:
    """Log the currently authenticated user out."""
    with sanitize_excs():
        await auth.logout_by_client_token(client_token)
    return success
