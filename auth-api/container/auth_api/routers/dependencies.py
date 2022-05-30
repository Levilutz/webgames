from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from auth_api import config
from auth_api.exceptions import NotFoundError
from auth_api.routers.utils import sanitize_excs
from auth_api.services import user_api


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{config.EXPECTED_PREFIX}/login")


def get_username(token: str = Depends(oauth2_scheme)) -> str:
    """Validate that a token is valid."""
    try:
        username = user_api.username_from_token(token)
    except NotFoundError:
        raise HTTPException(status_code=401, detail="Token invalid or expired")
    except Exception as e:
        with sanitize_excs():
            raise e
    return username


def get_token(token: str = Depends(oauth2_scheme)) -> str:
    """Validate that a token is valid."""
    # 401 / whatever else will propagate if necessary
    get_username(token)
    return token
