from pydantic import BaseModel


# Generic objects


class SuccessResponse(BaseModel):
    success: bool


# Endpoint objects


class RegisterRequest(BaseModel):
    username: str
    password: str


# Premade responses

success = SuccessResponse(success=True)
failure = SuccessResponse(success=False)
