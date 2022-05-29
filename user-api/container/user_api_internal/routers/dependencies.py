from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import UUID4

from user_api_internal import config
from user_api_internal.daos import User
from user_api_internal.internal import auth


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{config.EXPECTED_PREFIX}/login")


def fix_token(token: str) -> UUID4:
    """Convert token to UUID4 if it can."""
    try:
        return UUID4(token)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Malformed authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_token(token: str = Depends(oauth2_scheme)) -> UUID4:
    """Get a uuid from the client token string. No validation against db here."""
    token_uuid = fix_token(token)
    return token_uuid


async def get_user(token: UUID4 = Depends(get_token)) -> User:
    """Get a user from a client token string."""
    user = await auth.find_by_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Token invalid or expired")
    return user
