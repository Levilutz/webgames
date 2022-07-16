from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from auth_api import config
from auth_api.exceptions import NotFoundError
from auth_api.routers.utils import sanitize_excs
from auth_api.services import user_api


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{config.EXPECTED_PREFIX}/login")


def get_email_address(token: str = Depends(oauth2_scheme)) -> str:
    """Validate that a token is valid."""
    try:
        email_address = user_api.email_address_from_token(token)
    except NotFoundError:
        raise HTTPException(status_code=401, detail="Token invalid or expired")
    except Exception as e:
        with sanitize_excs():
            raise e
    return email_address


def get_token(token: str = Depends(oauth2_scheme)) -> str:
    """Validate that a token is valid."""
    # 401 / whatever else will propagate if necessary
    get_email_address(token)
    return token
