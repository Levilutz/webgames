import bcrypt
from contextlib import asynccontextmanager
import re
from secrets import randbelow
from typing import (
    Any,
    AsyncGenerator,
    AsyncContextManager,
    Callable,
    Dict,
    List,
)

from user_api.config import VERIFY_CODE_LENGTH
from user_api.daos import PreUser, get_db_connection
from user_api.exceptions import ClientError, InternalError, VerifyFailedError


legal_email_address_re = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
re_symbols = re.escape("`~!@#$%^&*()-=_+[]}{\\|;:'\",<.>/?")
legal_password_re = re.compile(f"^[a-zA-Z0-9{re_symbols}]{{8,72}}$")
legal_name_re = re.compile(r"^[a-zA-Z-]+$")
legal_verify_code_re = re.compile(f"^[0-9]{{{VERIFY_CODE_LENGTH}}}$")


def password_hash(password: str) -> str:
    """Use bcrypt to hash a password."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")


def password_verify(password: str, password_hash: str) -> bool:
    """Use bcrypt to verify a password"""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def legal_email_address(email_address: str) -> bool:
    """Is a given email address legal."""
    if email_address != email_address.lower():
        raise Exception("Email address should be lowercase by now")
    if len(email_address.encode("utf-8")) > 320:
        return False
    return re.match(legal_email_address_re, email_address) is not None


def legal_password(password: str) -> bool:
    """Is a given password legal."""
    # Validate it can be encoded to ≤72 bytes (since some chars become >1 byte in utf-8)
    if len(password.encode("utf-8")) > 72:
        return False
    return re.match(legal_password_re, password) is not None


def legal_name(name: str) -> bool:
    if len(name.encode("utf-8")) > 32:
        return False
    return re.match(legal_name_re, name) is not None


def legal_verify_code(verify_code: str) -> bool:
    return re.match(legal_verify_code_re, verify_code) is not None


def random_digits(length: int) -> str:
    """Securely generate a given number of digits as a string."""
    digits = [str(randbelow(10)) for i in range(length)]
    return "".join(digits)


async def increment_failed_attempts(email_address: str, amount: int = 1) -> None:
    """Increment the failed registration attempts for an email.

    This should be done in separate tx so the failure increment doesn't get trashed by
    the transaction rollback which will occur if ClientError or unexpected error occurs
    after increment.
    """
    async with await get_db_connection() as conn:
        pre_user = await PreUser.find_by_email_address(conn, email_address)
        if pre_user is None:
            raise InternalError(
                "Internal _increment_failed_attempts called with invalid PreUser"
            )

        await pre_user.increment_failed_attempts(conn, amount=amount)


def increments_failed_attempts(
    email_address: str,
) -> Callable[..., AsyncContextManager[None]]:
    """Generate context manager for a given email address."""

    email_address = email_address.lower()

    # Validate input is legal
    if not legal_email_address(email_address):
        raise ClientError("Invalid email address")

    @asynccontextmanager
    async def _increments_failed_attempts_inner(
        *args: List[Any], **kwargs: Dict[Any, Any]
    ) -> AsyncGenerator[None, None]:
        """Context manager to increment failed verification attempts as necessary.

        Any raised VerifyFailedErrors trigger failure increment and are re-raised as
        ClientErrors.
        """
        try:
            yield
        except VerifyFailedError as e:
            await increment_failed_attempts(email_address)
            raise ClientError(str(e))
        finally:
            pass

    return _increments_failed_attempts_inner
