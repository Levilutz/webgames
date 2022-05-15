from pydantic import BaseModel


# Generic objects


class SuccessResponse(BaseModel):
    success: bool


# Endpoint objects


class AuthLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    new_password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


# Premade responses

success = SuccessResponse(success=True)
failure = SuccessResponse(success=False)
