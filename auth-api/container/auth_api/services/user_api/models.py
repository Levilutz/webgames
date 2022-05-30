from pydantic import BaseModel


class LoginResponse(BaseModel):
    client_token: str


class TokenDataResponse(BaseModel):
    username: str
