from typing import Optional

from pydantic import BaseModel, UUID4


class PasswordResetCreateRequest(BaseModel):
    email_address: str


class PasswordResetCreateResponse(BaseModel):
    reset_code: Optional[UUID4]


class PreUserCreateRequest(BaseModel):
    email_address: str


class PreUserCreateResponse(BaseModel):
    verify_code: Optional[str]


class PreUserVerifyRequest(BaseModel):
    email_address: str
    verify_code: str


class TokenGetResponse(BaseModel):
    email_address: str


class UserCreateRequest(BaseModel):
    email_address: str
    password: str
    first_name: str
    last_name: str
    verify_code: str


class UserResetPasswordRequest(BaseModel):
    email_address: str
    password: str
    reset_code: UUID4


class UserLoginRequest(BaseModel):
    email_address: str
    password: str


class UserLoginResponse(BaseModel):
    client_token: str


class UserUpdateRequest(BaseModel):
    email_address: str
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
