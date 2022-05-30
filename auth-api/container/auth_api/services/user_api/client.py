from auth_api.services.user_api import models
from auth_api.services.user_api.utils import _request, _request_shaped


def register(username: str, password: str) -> None:
    """Register a new user."""
    body = {
        "password": password,
    }
    _request("POST", f"/users/{username}", body)


def change_password(username: str, password: str) -> None:
    """Change a user's password."""
    body = {
        "password": password,
    }
    _request("PUT", f"/users/{username}", body)


def delete_user(username: str) -> None:
    """Delete a user account."""
    _request("DELETE", f"/users/{username}")


def login(username: str, password: str) -> str:
    """Log a user in, return client_token if success."""
    body = {
        "password": password,
    }
    resp = _request_shaped(models.LoginResponse, "POST", f"/users/{username}", body)
    return resp.client_token


def logout(client_token: str) -> None:
    """Log a given token out."""
    _request("DELETE", f"/tokens/{client_token}")


def username_from_token(client_token: str) -> str:
    """Get the username associated with this token."""
    resp = _request_shaped(
        models.TokenDataResponse, "DELETE", f"/tokens/{client_token}"
    )
    return resp.username
