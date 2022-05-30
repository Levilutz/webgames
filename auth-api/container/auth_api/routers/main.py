from fastapi import Depends, FastAPI, Response, status
from fastapi.responses import PlainTextResponse
from fastapi.security import OAuth2PasswordRequestForm

from auth_api import config
from auth_api.routers import api_models, dependencies
from auth_api.routers.utils import sanitize_excs
from auth_api.services import user_api


app = FastAPI(root_path=config.EXPECTED_PREFIX)

success = Response(status_code=status.HTTP_200_OK)


@app.get("/ping", response_class=PlainTextResponse)
def ping() -> str:
    """Ping pong."""
    return "pong"


@app.post("/register")
def register(register_request: api_models.RegisterRequest) -> Response:
    """Register a new user."""
    with sanitize_excs():
        # Don't expand with ** to avoid leaking request params
        user_api.register(
            username=register_request.username,
            password=register_request.password,
        )
    return success


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()) -> api_models.LoginResponse:
    """Log a user in."""
    with sanitize_excs():
        # Don't expand with ** to avoid leaking request params
        client_token = user_api.login(
            username=form_data.username,
            password=form_data.password,
        )
    return api_models.LoginResponse(access_token=client_token)


@app.post("/login_json")
def login_json(
    login_request: api_models.LoginJsonRequest,
) -> api_models.LoginJsonResponse:
    """Log a user in, using json (non-oauth2-compliant endpoint)."""
    with sanitize_excs():
        # Don't expand with ** to avoid leaking request params
        client_token = user_api.login(
            username=login_request.username,
            password=login_request.password,
        )
    return api_models.LoginJsonResponse(client_token=client_token)


@app.post("/logout")
def logout(client_token: str = Depends(dependencies.get_token)) -> Response:
    """Log a currently logged-in user out."""
    with sanitize_excs():
        user_api.logout(client_token)
    return success


@app.post("/change_password")
def change_password(
    change_password_request: api_models.ChangePasswordRequest,
    username: str = Depends(dependencies.get_username),
) -> Response:
    """Change the currently authenticated user's password."""
    with sanitize_excs():
        user_api.change_password(username, change_password_request.password)
    return success


@app.post("/delete")
def delete_user(username: str = Depends(dependencies.get_username)) -> Response:
    """Delete the currently logged-in user."""
    with sanitize_excs():
        user_api.delete_user(username)
    return success
