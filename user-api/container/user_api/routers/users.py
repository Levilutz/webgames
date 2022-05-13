from fastapi import APIRouter

from user_api.internal import users
from user_api.routers import api_models
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
