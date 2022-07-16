from typing import Optional

from pydantic import BaseModel


class LoginResponse(BaseModel):
    client_token: str


class PreRegisterResponse(BaseModel):
    verify_code: Optional[str] = None


class RequestPasswordResetResponse(BaseModel):
    reset_code: Optional[str] = None


class TokenDataResponse(BaseModel):
    email_address: str
