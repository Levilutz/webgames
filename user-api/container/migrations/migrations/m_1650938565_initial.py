"""A single migration to run."""

from typing import Any

from psycopg import AsyncConnection

from migrations.migration import BaseMigration


class Migration(BaseMigration):
    """A base migration."""

    async def upgrade(self, conn: AsyncConnection[Any]) -> None:
        """Run the migration."""
        async with conn.cursor() as cur:
            # Create tables
            await cur.execute(
                """
                    CREATE TABLE pre_users (
                        email_address varchar(320) UNIQUE NOT NULL,
                        verify_code varchar(16) NOT NULL,
                        created_time timestamp NOT NULL,
                        failed_attempts integer
                    );
                    CREATE TABLE users (
                        user_id uuid PRIMARY KEY,
                        email_address varchar(320) UNIQUE NOT NULL,
                        password_hash varchar(60) NOT NULL,
                        first_name varchar(32) NOT NULL,
                        last_name varchar(32) NOT NULL,
                        created_time timestamp NOT NULL
                    );
                    CREATE TABLE sessions (
                        session_id uuid PRIMARY KEY,
                        client_token uuid NOT NULL UNIQUE,
                        user_id uuid REFERENCES users ON DELETE CASCADE,
                        created_time timestamp NOT NULL
                    );
                    CREATE INDEX ON sessions (user_id);
                """,
            )

    async def was_successful(self, conn: AsyncConnection[Any]) -> bool:
        """Check if the migration was successful.

        Function may return False to indicate generic error. You are encouraged to raise
        a descriptive exception inside the function instead. Both of these behaviors are
        handled in the runner.

        This function should _always_ return False / raise Exception if the migration
        did not run at all.
        """
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM users LIMIT 1")
            result = await cur.fetchall()
            assert result == []
        return True
