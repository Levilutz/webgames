from pydantic import BaseModel


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginJsonRequest(BaseModel):
    username: str
    password: str


class LoginJsonResponse(BaseModel):
    client_token: str


class ChangePasswordRequest(BaseModel):
    password: str
