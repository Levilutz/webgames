from typing import Optional

from pydantic import BaseModel


class ChangeLoginNotifyRequest(BaseModel):
    login_notify: bool


class ChangeNameRequest(BaseModel):
    first_name: str
    last_name: str


class ChangePasswordRequest(BaseModel):
    password: str


class LoginJsonRequest(BaseModel):
    email_address: str
    password: str


class LoginJsonResponse(BaseModel):
    client_token: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PreRegisterRequest(BaseModel):
    email_address: str


class PreRegisterResponse(BaseModel):
    verify_code: Optional[str]


class RegisterRequest(BaseModel):
    email_address: str
    password: str
    first_name: str
    last_name: str
    verify_code: str


class RequestResetPasswordRequest(BaseModel):
    email_address: str


class RequestResetPasswordResponse(BaseModel):
    reset_code: Optional[str]


class ResetPasswordRequest(BaseModel):
    email_address: str
    password: str
    reset_code: str
