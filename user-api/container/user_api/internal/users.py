import asyncio
from datetime import datetime
import re
from typing import Optional
from uuid import uuid4

import bcrypt
from pydantic import UUID4

from user_api.daos import Session, User, get_db_connection
from user_api.exceptions import UserError


legal_username_re = re.compile("^[a-zA-Z0-9][a-zA-Z0-9\\-_\\.]{2,32}$")
re_symbols = re.escape("`~!@#$%^&*()-=_+[]}{\\|;:'\",<.>/?")
legal_password_re = re.compile(f"^[a-zA-Z0-9{re_symbols}]{{8,72}}$")


def _password_hash(password: str) -> str:
    """Use bcrypt to hash a password."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")


def _password_verify(password: str, password_hash: str) -> bool:
    """Use bcrypt to verify a password"""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def _legal_username(username: str) -> bool:
    """Is a given username legal."""
    return re.match(legal_username_re, username) is not None


def _legal_password(password: str) -> bool:
    """Is a given password legal."""
    # Validate it can be encoded to ≤72 bytes (since some chars become >1 byte in utf-8)
    if len(password.encode("utf-8")) > 72:
        return False
    return re.match(legal_password_re, password) is not None


async def register(username: str, password: str) -> User:
    """Register a new user, return that User."""

    # Validate input is legal
    if not _legal_username(username):
        raise UserError("Invalid username")
    if not _legal_password(password):
        raise UserError("Invalid password")

    async with await get_db_connection() as conn:
        # Check username isn't claimed
        existing_user = await User.find_by_username(conn, username)
        if existing_user is not None:
            raise UserError(f"Username {username} already claimed")

        # Make a new user object
        new_user = User(
            user_id=uuid4(),
            username=username,
            password_hash=_password_hash(password),
        )

        # Insert the user into the database
        await new_user.create(conn)

    return new_user


async def change_password(username: str, new_password: str) -> None:
    """Change a user's password."""

    # Check new password is legal
    if not _legal_password(new_password):
        raise UserError("Invalid password")

    async with await get_db_connection() as conn:
        # Find the user
        user = await User.check_by_username(conn, username)

        # Update the user's password
        await user.update_password_hash(conn, _password_hash(new_password))


async def login(username: str, password: str) -> Session:
    """Attempt to a log a user in, return session if successful."""
    # Validate input is legal
    if not _legal_username(username):
        raise UserError("Invalid username")
    if not _legal_password(password):
        raise UserError("Invalid password")

    async with await get_db_connection() as conn:
        # Get the associated user
        user = await User.check_by_username(conn, username)

        # Validate the password
        if not _password_verify(password, user.password_hash):
            raise UserError("Invalid username or password")

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


async def logout(token_or_session_id: UUID4) -> None:
    """Log out a session, given either client token or session id."""
    async with await get_db_connection() as conn:
        # Find the session
        session = await Session.find_by_id(conn, token_or_session_id)
        if session is None:
            session = await Session.find_by_token(conn, token_or_session_id)
        if session is None:
            raise UserError("Failed to find given session")

        # Delete the session
        await session.delete(conn)


async def delete(username: str) -> None:
    """Delete a user account."""

    async with await get_db_connection() as conn:
        # Get the user
        user = await User.check_by_username(conn, username)

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


async def clean_sessions_loop() -> None:
    """Loop to clean sessions regularly."""
    while True:
        async with await get_db_connection() as conn:
            await Session.cleanup_expired(conn)
            await asyncio.sleep(3600)
