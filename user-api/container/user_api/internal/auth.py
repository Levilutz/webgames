import asyncio
from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import UUID4

from user_api.config import (
    ALLOWED_FAILED_VERIFICATIONS,
    EMAIL_ENABLED,
    VERIFY_CODE_LENGTH,
)
from user_api.daos import (
    PasswordReset,
    PreUser,
    Session,
    User,
    get_db_connection,
)
from user_api.exceptions import (
    ClientError,
    NotFoundError,
    VerifyFailedError,
)
from user_api.internal.utils import (
    increments_failed_attempts,
    legal_email_address,
    legal_name,
    legal_password,
    legal_verify_code,
    password_hash,
    password_verify,
    random_digits,
)
from user_api.services import email


async def preregister(email_address: str) -> PreUser:
    """Preregister a new user, return that pre-user."""

    email_address = email_address.lower()

    # Validate input is legal
    if not legal_email_address(email_address):
        raise ClientError("Invalid email address")

    async with await get_db_connection() as conn:
        # Check email isn't claimed
        existing_user = await User.find_by_email_address(conn, email_address)
        if existing_user is not None:
            raise ClientError(f"Email address {email_address} already claimed")

        # Find previous pre-registration attempt if it exists
        pre_user = await PreUser.find_by_email_address(conn, email_address)
        if pre_user is not None:
            # If allowed, send a new email and bump failed verifications
            if pre_user.failed_attempts >= ALLOWED_FAILED_VERIFICATIONS:
                raise ClientError("Maximum failed registrations for 24 hour period")
            await pre_user.update_verify_code(conn, random_digits(VERIFY_CODE_LENGTH))
            # There's mild potential for abuse here that needs to be fixed
            # If the user manages to trigger a failed attempt, but the func excs before
            # the end of the tx, the failure increment will be rolled back
            await pre_user.increment_failed_attempts(conn)

        else:
            # Make a new pre-user object
            pre_user = PreUser(
                email_address=email_address,
                verify_code=random_digits(VERIFY_CODE_LENGTH),
                created_time=datetime.utcnow(),
                failed_attempts=0,
            )

            # Insert the pre-user into the database
            await pre_user.create(conn)

        # Send verification email
        # Keep in context manager so we don't make pre-user if email blows up
        if EMAIL_ENABLED:
            email.send_verification_email(
                to_email=email_address,
                verify_code=pre_user.verify_code,
            )

    return pre_user


async def preregister_verify(email_address: str, verify_code: str) -> None:
    """Verify a given verification code. Throws execption if invalid."""

    email_address = email_address.lower()

    # Validate input is legal
    if not legal_email_address(email_address):
        raise ClientError("Invalid email address")
    if not legal_verify_code(verify_code):
        raise ClientError("Invalid verify code")

    async with increments_failed_attempts(email_address)():
        async with await get_db_connection() as conn:
            # Check verification code
            pre_user = await PreUser.find_by_email_address(conn, email_address)
            if pre_user is None:
                raise ClientError("Verification invalid or expired")
            if pre_user.failed_attempts >= ALLOWED_FAILED_VERIFICATIONS:
                raise ClientError("Maximum failed registrations for 24 hour period")
            if verify_code != pre_user.verify_code:
                raise VerifyFailedError("Verification code invalid")


async def register(
    email_address: str, password: str, first_name: str, last_name: str, verify_code: str
) -> User:
    """Register a new user, return that User."""

    email_address = email_address.lower()

    # Validate input is legal
    if not legal_email_address(email_address):
        raise ClientError("Invalid email address")
    if not legal_password(password):
        raise ClientError("Invalid password")
    if not legal_name(first_name):
        raise ClientError("Invalid first name")
    if not legal_name(last_name):
        raise ClientError("Invalid last name")
    if not legal_verify_code(verify_code):
        raise ClientError("Invalid verify code")

    async with increments_failed_attempts(email_address)():
        async with await get_db_connection() as conn:
            # Check email isn't claimed
            existing_user = await User.find_by_email_address(conn, email_address)
            if existing_user is not None:
                raise ClientError(f"Email address {email_address} already claimed")

            # Check verification code
            pre_user = await PreUser.find_by_email_address(conn, email_address)
            if pre_user is None:
                raise ClientError("Verification invalid or expired")

            if pre_user.failed_attempts >= ALLOWED_FAILED_VERIFICATIONS:
                raise ClientError("Maximum failed registrations for 24 hour period")

            if verify_code != pre_user.verify_code:
                raise VerifyFailedError("Verification code invalid")

            await pre_user.delete(conn)

            # Make a new user object
            new_user = User(
                user_id=uuid4(),
                email_address=email_address,
                password_hash=password_hash(password),
                first_name=first_name,
                last_name=last_name,
                created_time=datetime.utcnow(),
            )

            # Insert the user into the database
            await new_user.create(conn)

            # Send email welcoming the new user
            # Keep in context manager so we don't make user if email blows up
            if EMAIL_ENABLED:
                email.send_post_verification_email(
                    to_email=new_user.full_email(),
                    first_name=new_user.first_name,
                )

    return new_user


async def change_name(
    email_address: str, first_name: Optional[str], last_name: Optional[str]
) -> None:
    """Change a user's name."""
    if first_name is None and last_name is None:
        return

    email_address = email_address.lower()

    # Validate input
    if not legal_email_address(email_address):
        raise ClientError("Invalid email address")
    if first_name is not None and not legal_name(first_name):
        raise ClientError("Invalid first name")
    if last_name is not None and not legal_name(last_name):
        raise ClientError("Invalid last name")

    async with await get_db_connection() as conn:
        # Find the user
        user = await User.find_by_email_address(conn, email_address)
        if user is None:
            raise NotFoundError("Failed to find given user")

        # Update the user's name
        await user.update_name(
            conn,
            new_first_name=first_name or user.first_name,
            new_last_name=last_name or user.last_name,
        )


async def change_password(email_address: str, new_password: str) -> None:
    """Change a user's password."""

    email_address = email_address.lower()

    # Validate input
    if not legal_email_address(email_address):
        raise ClientError("Invalid email address")
    if not legal_password(new_password):
        raise ClientError("Invalid password")

    async with await get_db_connection() as conn:
        # Find the user
        user = await User.find_by_email_address(conn, email_address)
        if user is None:
            raise NotFoundError("Failed to find given user")

        # Update the user's password
        await user.update_password_hash(conn, password_hash(new_password))


async def request_reset_password(email_address: str) -> PasswordReset:
    """Request a password reset."""

    email_address = email_address.lower()

    # Validate input
    if not legal_email_address(email_address):
        raise ClientError("Invalid email address")

    async with await get_db_connection() as conn:
        # Find the user
        user = await User.find_by_email_address(conn, email_address)
        if user is None:
            raise NotFoundError("Failed to find given user")

        # Check if request already submitted
        password_reset = await PasswordReset.find_by_user_id(conn, user.user_id)
        if password_reset is not None:
            raise ClientError("Password reset request already pending")

        # Make a new password reset object
        password_reset = PasswordReset(
            reset_code=uuid4(),
            user_id=user.user_id,
            created_time=datetime.utcnow(),
        )

        # Insert the pre-user into the database
        await password_reset.create(conn)

        # Send email with the reset code
        # Keep in context manager so we don't make reset if email blows up
        if EMAIL_ENABLED:
            email.send_password_reset_email(
                to_email=user.full_email(),
                reset_code=str(password_reset.reset_code),
            )

    return password_reset


async def reset_password(
    email_address: str, new_password: str, reset_code: UUID4
) -> None:
    """Actually execute a password reset, provided the code is correct."""

    email_address = email_address.lower()

    # Validate input
    if not legal_email_address(email_address):
        raise ClientError("Invalid email address")
    if not legal_password(new_password):
        raise ClientError("Invalid password")

    async with await get_db_connection() as conn:
        # Find the user
        user = await User.find_by_email_address(conn, email_address)
        if user is None:
            raise NotFoundError("Failed to find given user")

        # Find the password reset
        password_reset = await PasswordReset.find_by_reset_code(conn, reset_code)
        if password_reset is None or password_reset.user_id != user.user_id:
            raise ClientError("Password reset code invalid")

        # Update the user's password
        await user.update_password_hash(conn, password_hash(new_password))

        # Remove the password reset request
        await password_reset.delete(conn)


async def login(email_address: str, password: str) -> Session:
    """Attempt to a log a user in, return session if successful."""

    email_address = email_address.lower()

    # Validate input
    if not legal_email_address(email_address):
        raise ClientError("Invalid email address")
    if not legal_password(password):
        raise ClientError("Invalid password")

    async with await get_db_connection() as conn:
        # Get the associated user
        user = await User.find_by_email_address(conn, email_address)

        if user is None:
            raise ClientError("Invalid email address or password")

        # Validate the password
        if not password_verify(password, user.password_hash):
            raise ClientError("Invalid email address or password")

        # Make a new session object
        new_session = Session(
            session_id=uuid4(),
            client_token=uuid4(),
            user_id=user.user_id,
            created_time=datetime.utcnow(),
        )

        # Insert the session into the database
        await new_session.create(conn)

    return new_session


async def logout_by_session_id(session_id: UUID4) -> None:
    """Log out a session given a client token."""
    async with await get_db_connection() as conn:
        # Find the session
        session = await Session.find_by_id(conn, session_id)
        if session is None:
            raise NotFoundError("Failed to find given session")

        # Delete the session
        await session.delete(conn)


async def logout_by_client_token(client_token: UUID4) -> None:
    """Log out a session given a client token."""
    async with await get_db_connection() as conn:
        # Find the session
        session = await Session.find_by_token(conn, client_token)
        if session is None:
            raise NotFoundError("Failed to find given session")

        # Delete the session
        await session.delete(conn)


async def delete(email_address: str) -> None:
    """Delete a user account."""

    email_address = email_address.lower()

    # Validate input
    if not legal_email_address(email_address):
        raise ClientError("Invalid email address")

    async with await get_db_connection() as conn:
        # Get the user
        user = await User.find_by_email_address(conn, email_address)
        if user is None:
            raise NotFoundError("Failed to find given user")

        # Delete the user
        await user.delete(conn)


async def find_by_token(client_token: UUID4) -> Optional[User]:
    """Find a user by a client token."""

    async with await get_db_connection() as conn:
        # Find the session
        session = await Session.find_by_token(conn, client_token)

        if session is None:
            return None

        # Find the user and return
        return await User.find_by_id(conn, session.user_id)


async def clean_db_loop() -> None:
    """Loop to clean db stuff regularly."""
    while True:
        async with await get_db_connection() as conn:
            await PasswordReset.cleanup_expired(conn)
            await PreUser.cleanup_expired(conn)
            await Session.cleanup_expired(conn)
            await asyncio.sleep(3600)
