from pydantic import BaseModel


class AuthLoginResponse(BaseModel):
    client_token: str


class UserCreateRequest(BaseModel):
    password: str


class UserUpdateRequest(BaseModel):
    password: str


class UserLoginRequest(BaseModel):
    password: str
