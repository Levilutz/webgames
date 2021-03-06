"""Base migration class."""

from typing import Any

from psycopg import AsyncConnection


class BaseMigration(object):
    """A single migration."""

    async def upgrade(self, conn: AsyncConnection[Any]) -> None:
        """Run the migration."""
        raise NotImplementedError()

    async def was_successful(self, conn: AsyncConnection[Any]) -> bool:
        """Check if the migration was successful.

        Function may return False to indicate generic error. You are encouraged to raise
        a descriptive exception inside the function instead. Both of these behaviors are
        handled in the runner.

        This function should _always_ return False / raise Exception if the migration
        did not run at all.
        """
        raise NotImplementedError()
