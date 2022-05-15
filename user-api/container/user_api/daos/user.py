from __future__ import annotations  # Postponed annotation evaluation, remove once 3.11

from typing import Optional

from psycopg.rows import class_row
from pydantic import BaseModel, UUID4

from user_api.daos.database import AsyncConnection
from user_api.exceptions import InternalError


class User(BaseModel):
    user_id: UUID4
    username: str
    password_hash: str

    async def create(self, conn: AsyncConnection) -> None:
        """Create the current user in the database."""
        if await self.find_by_id(conn, self.user_id) is not None:
            raise InternalError(
                f"Cannot create User - id {self.user_id} already exists"
            )
        if await self.find_by_username(conn, self.username) is not None:
            raise InternalError(f"Cannot create User - username {self.username} taken")

        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO users VALUES (%s, %s, %s)",
                tuple(self.dict().values()),
            )

    async def update_username(self, conn: AsyncConnection, new_username: str) -> None:
        """Update the user's username if possible."""
        await self.check_by_id(conn, self.user_id)

        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE users SET username = %s WHERE user_id = %s",
                (new_username, self.user_id),
            )

        self.username = new_username

    async def update_password_hash(
        self, conn: AsyncConnection, new_password_hash: str
    ) -> None:
        """Update the user's password if possible."""
        await self.check_by_id(conn, self.user_id)

        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE users SET password_hash = %s WHERE user_id = %s",
                (new_password_hash, self.user_id),
            )

        self.password_hash = new_password_hash

    async def delete(self, conn: AsyncConnection) -> None:
        """Delete the current user from the database."""
        await self.check_by_id(conn, self.user_id)

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
    async def find_by_username(
        cls, conn: AsyncConnection, username: str
    ) -> Optional[User]:
        """Find a user by username."""
        async with conn.cursor(row_factory=class_row(User)) as cur:
            await cur.execute(
                "SELECT * FROM users WHERE username = %s",
                (username,),
            )
            return await cur.fetchone()

    @classmethod
    async def check_by_id(cls, conn: AsyncConnection, user_id: UUID4) -> User:
        """Raise exception if the user id doesn't exist."""
        user = await cls.find_by_id(conn, user_id)
        if user is None:
            raise InternalError(f"Cannot find User - id {user_id} does not exist")
        return user

    @classmethod
    async def check_by_username(cls, conn: AsyncConnection, username: str) -> User:
        """Raise exception if the user id doesn't exist."""
        user = await cls.find_by_username(conn, username)
        if user is None:
            raise InternalError(
                f"Cannot find User - username {username} does not exist"
            )
        return user
