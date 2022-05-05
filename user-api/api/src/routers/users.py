from fastapi import APIRouter

from internal import users

from routers import api_models
from routers.utils import sanitize_excs


router = APIRouter()


@router.get("/register")
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
