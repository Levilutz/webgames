from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import UUID4

from user_api import config


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
