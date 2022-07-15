from __future__ import annotations  # Postponed annotation evaluation, remove once 3.11

from datetime import datetime
from typing import Optional

from psycopg.rows import class_row
from pydantic import BaseModel, UUID4

from user_api.daos.database import AsyncConnection
from user_api.daos.utils import _verify_email_lowercase
from user_api.exceptions import InternalError


class User(BaseModel):
    """A registered user."""

    user_id: UUID4
    email_address: str
    password_hash: str
    first_name: str
    last_name: str
    created_time: datetime

    async def create(self, conn: AsyncConnection) -> None:
        """Create the current user in the database."""
        _verify_email_lowercase(self.email_address)

        if await self.find_by_id(conn, self.user_id) is not None:
            raise InternalError(
                f"Cannot create User - id {self.user_id} already exists"
            )
        if await self.find_by_email_address(conn, self.email_address) is not None:
            raise InternalError(
                f"Cannot create User - email address {self.email_address} taken"
            )

        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s)",
                tuple(self.dict().values()),
            )

    async def update_email_address(
        self, conn: AsyncConnection, new_email_address: str
    ) -> None:
        """Update the user's email address if possible."""
        _verify_email_lowercase(new_email_address)
        _verify_email_lowercase(self.email_address)

        await self.assert_exists(conn)

        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE users SET email_address = %s WHERE user_id = %s",
                (new_email_address, self.user_id),
            )

        self.email_address = new_email_address

    async def update_name(
        self, conn: AsyncConnection, new_first_name: str, new_last_name: str
    ) -> None:
        """Update the user's name if possible."""
        await self.assert_exists(conn)

        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE users SET first_name = %s, last_name = %s WHERE user_id = %s",
                (new_first_name, new_last_name, self.user_id),
            )

        self.first_name = new_first_name
        self.last_name = new_last_name

    async def update_password_hash(
        self, conn: AsyncConnection, new_password_hash: str
    ) -> None:
        """Update the user's password if possible."""
        await self.assert_exists(conn)

        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE users SET password_hash = %s WHERE user_id = %s",
                (new_password_hash, self.user_id),
            )

        self.password_hash = new_password_hash

    async def delete(self, conn: AsyncConnection) -> None:
        """Delete the current user from the database."""
        await self.assert_exists(conn)

        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM users WHERE user_id = %s",
                (self.user_id,),
            )

    @classmethod
    async def find_by_id(cls, conn: AsyncConnection, user_id: UUID4) -> Optional[User]:
        """Find a user by id."""
        async with conn.cursor(row_factory=class_row(User)) as cur:
            await cur.execute(
                "SELECT * FROM users WHERE user_id = %s",
                (user_id,),
            )
            return await cur.fetchone()

    @classmethod
    async def find_by_email_address(
        cls, conn: AsyncConnection, email_address: str
    ) -> Optional[User]:
        """Find a user by email address."""
        _verify_email_lowercase(email_address)

        async with conn.cursor(row_factory=class_row(User)) as cur:
            await cur.execute(
                "SELECT * FROM users WHERE email_address = %s",
                (email_address,),
            )
            return await cur.fetchone()

    async def assert_exists(self, conn: AsyncConnection) -> None:
        """Raise exception if the user id doesn't exist."""
        _verify_email_lowercase(self.email_address)

        user = await self.find_by_id(conn, self.user_id)
        if user is None:
            raise InternalError(
                "User does not exist in db, should have been checked earlier"
            )

        # Complain on any differences from db
        if (
            self.user_id != user.user_id
            or self.email_address != user.email_address
            or self.password_hash != user.password_hash
            or self.first_name != user.first_name
            or self.last_name != user.last_name
            or self.created_time != user.created_time
        ):
            raise InternalError(f"User deviation from db: {self} vs {user}")

    def full_email(self) -> str:
        """Get the full email for the given user."""
        return f"{self.first_name} {self.last_name} <{self.email_address}>"
