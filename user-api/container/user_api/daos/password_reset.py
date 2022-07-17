from __future__ import annotations  # Postponed annotation evaluation, remove once 3.11

from datetime import datetime, timedelta
from typing import Optional

from psycopg.rows import class_row
from pydantic import BaseModel, UUID4

from user_api.config import PASSWORD_RESET_TTL_HOURS
from user_api.daos.database import AsyncConnection
from user_api.exceptions import InternalError


class PasswordReset(BaseModel):
    reset_code: UUID4
    user_id: UUID4
    created_time: datetime

    async def create(self, conn: AsyncConnection) -> None:
        """Create the current password_reset in the database."""
        if await self.find_by_reset_code(conn, self.reset_code) is not None:
            raise InternalError(
                f"Cannot create PasswordReset - code {self.reset_code} already claimed"
            )

        if await self.find_by_user_id(conn, self.user_id) is not None:
            raise InternalError(
                f"Cannot create PasswordReset - user {self.user_id} already resetting"
            )

        async with conn.cursor() as cur:
            # Clean up expired for this user_id if necessary
            latest_valid = datetime.utcnow() - timedelta(hours=PASSWORD_RESET_TTL_HOURS)
            await cur.execute(
                "DELETE FROM password_resets WHERE user_id = %s AND created_time <= %s",
                (self.user_id, latest_valid),
            )

            # Create the new password reset
            await cur.execute(
                "INSERT INTO password_resets VALUES (%s, %s, %s)",
                (tuple(self.dict().values())),
            )

    async def delete(self, conn: AsyncConnection) -> None:
        """Delete the current password reset from the database."""
        await self.assert_exists(conn)

        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM password_resets WHERE reset_code = %s",
                (self.reset_code,),
            )

    async def assert_exists(self, conn: AsyncConnection) -> None:
        """Raise exception of the password reset doesn't exist."""
        password_reset = await self.find_by_reset_code(conn, self.reset_code)
        if password_reset is None:
            raise InternalError(
                "Password reset does not exist in db, should have been checked earlier"
            )

        # Complain on any differences from db
        if (
            self.reset_code != password_reset.reset_code
            or self.user_id != password_reset.user_id
            or self.created_time != password_reset.created_time
        ):
            raise InternalError(
                f"PasswordReset deviation from db: {self} vs {password_reset}"
            )

    @classmethod
    async def find_by_reset_code(
        cls, conn: AsyncConnection, reset_code: UUID4
    ) -> Optional[PasswordReset]:
        """Find a password reset by code."""
        async with conn.cursor(row_factory=class_row(PasswordReset)) as cur:
            await cur.execute(
                "SELECT * FROM password_resets WHERE reset_code = %s",
                (reset_code,),
            )
            password_reset = await cur.fetchone()
            if (
                password_reset is None
                or password_reset.expiry_time() < datetime.utcnow()
            ):
                return None
            return password_reset

    @classmethod
    async def find_by_user_id(
        cls, conn: AsyncConnection, user_id: UUID4
    ) -> Optional[PasswordReset]:
        """Find a password reset by code."""
        async with conn.cursor(row_factory=class_row(PasswordReset)) as cur:
            await cur.execute(
                "SELECT * FROM password_resets WHERE user_id = %s",
                (user_id,),
            )
            password_reset = await cur.fetchone()
            if (
                password_reset is None
                or password_reset.expiry_time() < datetime.utcnow()
            ):
                return None
            return password_reset

    @classmethod
    async def cleanup_expired(cls, conn: AsyncConnection) -> None:
        """Clean up expired password resets."""
        latest_valid = datetime.utcnow() - timedelta(hours=PASSWORD_RESET_TTL_HOURS)
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM password_resets WHERE created_time <= %s",
                (latest_valid,),
            )

    def expiry_time(self) -> datetime:
        """Get the password reset's expiration time."""
        return self.created_time + timedelta(hours=PASSWORD_RESET_TTL_HOURS)
