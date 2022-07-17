from __future__ import annotations  # Postponed annotation evaluation, remove once 3.11

from datetime import datetime, timedelta
from typing import Optional

from psycopg.rows import class_row
from pydantic import BaseModel

from user_api.config import PREUSER_TTL_HOURS
from user_api.daos.database import AsyncConnection
from user_api.daos.utils import _verify_email_lowercase
from user_api.exceptions import InternalError


class PreUser(BaseModel):
    """A user that hasn't verified yet."""

    email_address: str
    verify_code: str
    created_time: datetime
    failed_attempts: int

    async def create(self, conn: AsyncConnection) -> None:
        """Create the current pre-user in the database."""
        _verify_email_lowercase(self.email_address)

        if await self.find_by_email_address(conn, self.email_address) is not None:
            raise InternalError(
                f"Cannot create PreUser - email {self.email_address} already exists"
            )

        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO pre_users VALUES (%s, %s, %s, %s)",
                tuple(self.dict().values()),
            )

    async def update_verify_code(self, conn: AsyncConnection, verify_code: str) -> None:
        """Update the verification code."""
        _verify_email_lowercase(self.email_address)

        await self.assert_exists(conn)

        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE pre_users SET verify_code = %s WHERE email_address = %s",
                (verify_code, self.email_address),
            )

        self.verify_code = verify_code

    async def increment_failed_attempts(
        self, conn: AsyncConnection, amount: int = 1
    ) -> None:
        """Increment the failed attempts by the given amount, defaulting to 1."""
        _verify_email_lowercase(self.email_address)

        await self.assert_exists(conn)

        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE pre_users SET failed_attempts = %s WHERE email_address = %s",
                (self.failed_attempts + amount, self.email_address),
            )

        self.failed_attempts += amount

    async def delete(self, conn: AsyncConnection) -> None:
        """Delete the current pre-user from the database."""
        _verify_email_lowercase(self.email_address)

        await self.assert_exists(conn)

        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM pre_users WHERE email_address = %s",
                (self.email_address,),
            )

    @classmethod
    async def find_by_email_address(
        cls, conn: AsyncConnection, email_address: str
    ) -> Optional[PreUser]:
        """Find a pre-user by email address."""
        _verify_email_lowercase(email_address)

        async with conn.cursor(row_factory=class_row(PreUser)) as cur:
            await cur.execute(
                "SELECT * FROM pre_users WHERE email_address = %s",
                (email_address,),
            )
            pre_user = await cur.fetchone()
            if pre_user is None or pre_user.expiry_time() < datetime.utcnow():
                return None
            return pre_user

    async def assert_exists(self, conn: AsyncConnection) -> None:
        """Raise exception if the email address doesn't exist."""
        _verify_email_lowercase(self.email_address)

        pre_user = await self.find_by_email_address(conn, self.email_address)
        if pre_user is None:
            raise InternalError(
                "PreUser does not exist in db, should have been checked earlier"
            )

        # Complain on any differences from db
        if (
            self.email_address != pre_user.email_address
            or self.verify_code != pre_user.verify_code
            or self.created_time != pre_user.created_time
            or self.failed_attempts != pre_user.failed_attempts
        ):
            raise InternalError(f"PreUser deviation from db: {self} vs {pre_user}")

    @classmethod
    async def cleanup_expired(cls, conn: AsyncConnection) -> None:
        """Clean up expired pre-users."""
        latest_valid = datetime.utcnow() - timedelta(hours=PREUSER_TTL_HOURS)
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM pre_users WHERE created_time < %s",
                (latest_valid,),
            )

    def expiry_time(self) -> datetime:
        """Get the pre-user's expiry time."""
        return self.created_time + timedelta(hours=PREUSER_TTL_HOURS)
