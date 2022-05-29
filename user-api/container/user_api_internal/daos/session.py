from __future__ import annotations  # Postponed annotation evaluation, remove once 3.11

from datetime import datetime, timedelta
from typing import Optional

from psycopg.rows import class_row
from pydantic import BaseModel, UUID4

from user_api_internal.daos.database import AsyncConnection
from user_api_internal.exceptions import InternalError


SESSION_TTL_HOURS = 12


class Session(BaseModel):
    session_id: UUID4
    client_token: UUID4
    user_id: UUID4
    created_time: datetime

    async def create(self, conn: AsyncConnection) -> None:
        """Create the current session in the database."""
        if await self.find_by_id(conn, self.session_id) is not None:
            raise InternalError(
                f"Cannot create Session - id {self.session_id} already exists"
            )

        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO sessions VALUES (%s, %s, %s, %s)",
                (tuple(self.dict().values())),
            )

    async def delete(self, conn: AsyncConnection) -> None:
        """Delete the current session."""
        await self.check_by_id(conn, self.session_id)

        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM sessions WHERE session_id = %s",
                (self.session_id,),
            )

    @classmethod
    async def find_by_id(
        cls, conn: AsyncConnection, session_id: UUID4
    ) -> Optional[Session]:
        """Find a session by id."""
        async with conn.cursor(row_factory=class_row(Session)) as cur:
            await cur.execute(
                "SELECT * FROM sessions WHERE session_id = %s",
                (session_id,),
            )
            sess = await cur.fetchone()
            if sess is None or sess.expiry_time() < datetime.utcnow():
                return None
            return sess

    @classmethod
    async def find_by_token(
        cls, conn: AsyncConnection, client_token: UUID4
    ) -> Optional[Session]:
        """Find a session by client token."""
        async with conn.cursor(row_factory=class_row(Session)) as cur:
            await cur.execute(
                "SELECT * FROM sessions WHERE client_token = %s",
                (client_token,),
            )
            sess = await cur.fetchone()
            if sess is None or sess.expiry_time() < datetime.utcnow():
                return None
            return sess

    @classmethod
    async def check_by_id(cls, conn: AsyncConnection, session_id: UUID4) -> Session:
        """Raise exception if the session doesn't exist."""
        session = await cls.find_by_id(conn, session_id)
        if session is None:
            raise InternalError(f"Cannot find Session - id {session_id} does not exist")
        return session

    @classmethod
    async def check_by_token(
        cls, conn: AsyncConnection, client_token: UUID4
    ) -> Session:
        """Raise exception if the session doesn't exist."""
        session = await cls.find_by_token(conn, client_token)
        if session is None:
            raise InternalError(
                f"Cannot find Session - token {client_token} does not exist"
            )
        return session

    @classmethod
    async def cleanup_expired(cls, conn: AsyncConnection) -> None:
        """Clean up expired sessions."""
        latest_valid = datetime.utcnow() - timedelta(hours=SESSION_TTL_HOURS)
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM sessions WHERE created_time <= %s",
                (latest_valid,),
            )

    def expiry_time(self) -> datetime:
        """Get the session's expiration time."""
        return self.created_time + timedelta(hours=SESSION_TTL_HOURS)
