from typing import Optional

from auth_api.services.user_api import models
from auth_api.services.user_api.utils import _request, _request_shaped


def preregister(email_address: str) -> Optional[str]:
    """Pre-register a new user, submitting their email for verification."""
    body = {
        "email_address": email_address,
    }
    resp = _request_shaped(models.PreRegisterResponse, "POST", "/pre_users", body)
    return resp.verify_code  # Will be None in prod, but actual code in testing / dev


def preregister_verify(email_address: str, verify_code: str) -> None:
    """Check the email verify code, throws relevant exc if bad."""
    body = {
        "email_address": email_address,
        "verify_code": verify_code,
    }
    _request("POST", "/pre_users/verify", body)


def register(
    email_address: str, password: str, first_name: str, last_name: str, verify_code: str
) -> None:
    """Register a new user."""
    body = {
        "email_address": email_address,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "verify_code": verify_code,
    }
    _request("POST", "/users", body)


def change_password(email_address: str, password: str) -> None:
    """Change a user's password."""
    body = {
        "email_address": email_address,
        "password": password,
    }
    _request("PUT", "/users", body)


def change_name(email_address: str, first_name: str, last_name: str) -> None:
    """Change a user's name."""
    body = {
        "email_address": email_address,
        "first_name": first_name,
        "last_name": last_name,
    }
    _request("PUT", "/users", body)


def delete_user(email_address: str) -> None:
    """Delete a user account."""
    body = {
        "email_address": email_address,
    }
    _request("DELETE", "/users", body)


def login(email_address: str, password: str) -> str:
    """Log a user in, return client_token if success."""
    body = {
        "email_address": email_address,
        "password": password,
    }
    resp = _request_shaped(models.LoginResponse, "POST", "/users/login", body)
    return resp.client_token


def logout(client_token: str) -> None:
    """Log a given token out."""
    _request("DELETE", f"/tokens/{client_token}")


def email_address_from_token(client_token: str) -> str:
    """Get the email address associated with this token."""
    resp = _request_shaped(models.TokenDataResponse, "GET", f"/tokens/{client_token}")
    return resp.email_address
