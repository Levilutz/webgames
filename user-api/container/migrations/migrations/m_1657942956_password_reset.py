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
                    CREATE TABLE password_resets (
                        reset_code uuid PRIMARY KEY,
                        user_id uuid UNIQUE REFERENCES users ON DELETE CASCADE,
                        created_time timestamp NOT NULL
                    );
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
        return True
