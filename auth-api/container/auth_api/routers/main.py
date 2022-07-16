from fastapi import Depends, FastAPI, Response, status
from fastapi.responses import PlainTextResponse
from fastapi.security import OAuth2PasswordRequestForm

from auth_api import config
from auth_api.routers import api_models, dependencies
from auth_api.routers.utils import sanitize_excs
from auth_api.services import user_api


app = FastAPI(root_path=config.EXPECTED_PREFIX)

success = Response(status_code=status.HTTP_200_OK)


@app.on_event("startup")
async def app_startup() -> None:
    """Verify config, start background tasks."""
    # Validate env vars set
    if any([var is None for var in config.REQUIRED_ENV_FOR_DEPLOY]):
        raise Exception(f"Missing required env vars: {config.REQUIRED_ENV_FOR_DEPLOY}")


@app.get("/ping", response_class=PlainTextResponse)
def ping() -> str:
    """Ping pong."""
    return "pong"


@app.post("/preregister")
def preregister(
    pre_register_request: api_models.PreRegisterRequest,
) -> api_models.PreRegisterResponse:
    """Pre-register a new user, subitting their email for verification."""
    with sanitize_excs():
        verify_code = user_api.preregister(
            email_address=pre_register_request.email_address
        )
        resp = api_models.PreRegisterResponse(verify_code=verify_code)
    return resp


@app.get("/preregister")
def preregister_verify(email_address: str, verify_code: str) -> Response:
    """Verify a pre-registration email code."""
    with sanitize_excs():
        # Throws back exc if failed to verify
        user_api.preregister_verify(
            email_address=email_address,
            verify_code=verify_code,
        )
    return success


@app.post("/register")
def register(register_request: api_models.RegisterRequest) -> Response:
    """Register a new user."""
    with sanitize_excs():
        # Don't expand with ** to avoid leaking request params
        user_api.register(
            email_address=register_request.email_address,
            password=register_request.password,
            first_name=register_request.first_name,
            last_name=register_request.last_name,
            verify_code=register_request.verify_code,
        )
    return success


@app.post("/request_reset_password")
def request_reset_password(
    request_reset_password_request: api_models.RequestResetPasswordRequest,
) -> api_models.RequestResetPasswordResponse:
    """Request a password reset."""
    with sanitize_excs():
        # Don't expand with ** to avoid leaking request params
        reset_code = user_api.request_reset_password(
            email_address=request_reset_password_request.email_address,
        )
        resp = api_models.RequestResetPasswordResponse(reset_code=reset_code)
    return resp


@app.post("/reset_password")
def reset_password(reset_password_request: api_models.ResetPasswordRequest) -> Response:
    """Reset a user's password."""
    with sanitize_excs():
        # Don't expand with ** to avoid leaking request params
        user_api.reset_password(
            email_address=reset_password_request.email_address,
            new_password=reset_password_request.password,
            reset_code=reset_password_request.reset_code,
        )
    return success


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()) -> api_models.LoginResponse:
    """Log a user in."""
    with sanitize_excs():
        # Don't expand with ** to avoid leaking request params
        client_token = user_api.login(
            email_address=form_data.username,
            password=form_data.password,
        )
        resp = api_models.LoginResponse(access_token=client_token)
    return resp


@app.post("/login_json")
def login_json(
    login_request: api_models.LoginJsonRequest,
) -> api_models.LoginJsonResponse:
    """Log a user in, using json (non-oauth2-compliant endpoint)."""
    with sanitize_excs():
        # Don't expand with ** to avoid leaking request params
        client_token = user_api.login(
            email_address=login_request.email_address,
            password=login_request.password,
        )
        resp = api_models.LoginJsonResponse(client_token=client_token)
    return resp


@app.post("/logout")
def logout(client_token: str = Depends(dependencies.get_token)) -> Response:
    """Log a currently logged-in user out."""
    with sanitize_excs():
        user_api.logout(client_token=client_token)
    return success


@app.get("/user_data")
def get_user_data(
    email_address: str = Depends(dependencies.get_email_address),
) -> api_models.GetUserDataResponse:
    """Get the currently authenticated user's basic data."""
    with sanitize_excs():
        user_data = user_api.get_user(email_address=email_address)
        resp = api_models.GetUserDataResponse(
            email_address=user_data.email_address,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            login_notify=user_data.login_notify,
        )
    return resp


@app.post("/change_password")
def change_password(
    change_password_request: api_models.ChangePasswordRequest,
    email_address: str = Depends(dependencies.get_email_address),
) -> Response:
    """Change the currently authenticated user's password."""
    with sanitize_excs():
        user_api.change_password(
            email_address=email_address,
            password=change_password_request.password,
        )
    return success


@app.post("/change_name")
def change_name(
    change_name_request: api_models.ChangeNameRequest,
    email_address: str = Depends(dependencies.get_email_address),
) -> Response:
    """Change the currently authenticated user's name."""
    with sanitize_excs():
        user_api.change_name(
            email_address=email_address,
            first_name=change_name_request.first_name,
            last_name=change_name_request.last_name,
        )
    return success


@app.post("/change_login_notify")
def change_login_notify(
    change_login_notify_request: api_models.ChangeLoginNotifyRequest,
    email_address: str = Depends(dependencies.get_email_address),
) -> Response:
    """Change the currently authenticated user's login notification setting."""
    with sanitize_excs():
        user_api.change_login_notify(
            email_address=email_address,
            login_notify=change_login_notify_request.login_notify,
        )
    return success


@app.post("/delete")
def delete_user(
    email_address: str = Depends(dependencies.get_email_address),
) -> Response:
    """Delete the currently logged-in user."""
    with sanitize_excs():
        user_api.delete_user(email_address=email_address)
    return success
