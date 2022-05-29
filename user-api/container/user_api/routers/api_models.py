from pydantic import BaseModel


class AuthLoginResponse(BaseModel):
    client_token: str


class ChangePasswordRequest(BaseModel):
    new_password: str


class AuthRequest(BaseModel):
    username: str
    password: str


class UserCreateRequest(BaseModel):
    password: str


class UserLoginRequest(BaseModel):
    password: str
