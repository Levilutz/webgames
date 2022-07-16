from typing import Optional

from pydantic import BaseModel


class GetUserResponse(BaseModel):
    email_address: str
    first_name: str
    last_name: str
    login_notify: bool


class LoginResponse(BaseModel):
    client_token: str


class PreRegisterResponse(BaseModel):
    verify_code: Optional[str] = None


class RequestPasswordResetResponse(BaseModel):
    reset_code: Optional[str] = None


class TokenDataResponse(BaseModel):
    email_address: str
