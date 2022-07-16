from typing import Optional

from pydantic import BaseModel


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
