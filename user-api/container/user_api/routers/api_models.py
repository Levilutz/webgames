from pydantic import BaseModel


class AuthLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthLoginResponseSimple(BaseModel):
    client_token: str


class ChangePasswordRequest(BaseModel):
    new_password: str


class AuthRequest(BaseModel):
    username: str
    password: str


class UserCreateRequest(BaseModel):
    password: str
