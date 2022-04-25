#!/usr/bin/env python3

import asyncio
import importlib
import os
import re
import time
from typing import Any, Dict, List

import psycopg

from migrations.migration import BaseMigration


async def get_db_connection() -> psycopg.AsyncConnection[Any]:
    """Get a new db connection."""
    # Extract from env vars
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_address = os.getenv("DB_ADDRESS")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    # Create and return the connection
    conn = await psycopg.AsyncConnection.connect(
        user=db_user,
        password=db_pass,
        host=db_address,
        port=db_port,
        dbname=db_name,
    )

    return conn


async def wait_for_live(timeout: int = 60) -> None:
    """Wait for the db to come alive with the desired creds."""
    start_t = time.time()
    success = False
    while time.time() - start_t < timeout:
        print("Attempting connection")
        try:
            async with await get_db_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
                    res = await cur.fetchall()
                    if res != [(1,)]:
                        raise Exception(f"Unexpected result: {res}")
            print("Connected succesfully")
            success = True
            break
        except Exception as e:
            print(f"Failed to connect: {e}")
        await asyncio.sleep(1)
    if not success:
        raise Exception(f"Failed to connect in {timeout}s")


def time_from_migration_name(migration_name: str) -> int:
    """Get creation time from the migration name."""
    time_re = re.compile(r"^m_(\d+)_")
    match = re.search(time_re, migration_name)
    if match is None:
        raise Exception(f"Failed to get time from migration {migration_name}")
    return int(match[1])


def get_code_migrations() -> Dict[str, BaseMigration]:
    """Collect all migrations in folder."""
    mig_re = re.compile(r"^m_\d+_[a-zA-Z0-9\-_]+\.py$")
    filenames = [fn for fn in os.listdir("migrations") if re.match(mig_re, fn)]

    out_migrations: Dict[str, BaseMigration] = {}
    for fn in filenames:
        # Get the migration name
        migration_name = fn[:-3]

        # Get the migration object
        module = importlib.import_module(f"migrations.{migration_name}")
        assert hasattr(module, "Migration"), f"No Migration in file {fn}"
        migration = module.Migration()
        assert isinstance(migration, BaseMigration), f"Wrong type from file {fn}"

        out_migrations[migration_name] = migration

    return out_migrations


async def check_db_migrations() -> bool:
    """Check if migrations exist in the db yet, return False if they do not."""
    try:
        async with await get_db_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM migrations")
    except psycopg.errors.UndefinedTable:
        return False
    # Propogate any other unexpected errors
    return True


async def create_db_migrations() -> None:
    """Create the migrations table in the db."""
    async with await get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "CREATE TABLE migrations (migrationid varchar(255) PRIMARY KEY)"
            )


async def get_db_migrations() -> List[str]:
    """Collect all migrations that have already run in the db."""
    async with await get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM migrations")
            res = await cur.fetchall()
    if res is None:
        raise Exception("Failed to get from db, no exception")
    return [row[0] for row in res]


def compute_needed_migrations(
    code_migrations: List[str], db_migrations: List[str]
) -> List[str]:
    """Get what migrations should be run, given those in code and those in the db.

    Output is ordered, with migrations to run first at the start of the list.
    """
    unknown = list(set(db_migrations) - set(code_migrations))
    if unknown:
        raise Exception(f"Found unknown migrations: {unknown}")

    needed = list(set(code_migrations) - set(db_migrations))
    needed.sort(key=time_from_migration_name)

    if code_migrations and db_migrations:
        latest_db_migration = max(map(time_from_migration_name, db_migrations))
        expired = [
            migr
            for migr in needed
            if time_from_migration_name(migr) < latest_db_migration
        ]
        if expired:
            raise Exception(f"Found expired migrations: {expired}")

    return needed


async def run_migration(migration_name: str, migration: BaseMigration) -> None:
    """Run a single migration."""
    print(f"Running migration {migration_name}")

    async with await get_db_connection() as conn:
        await migration.upgrade(conn)
        if not await migration.was_successful(conn):
            raise Exception("Migration failed")
        async with conn.cursor() as cur:
            await cur.execute("INSERT INTO migrations VALUES (%s)", (migration_name,))

    print(f"Completed migration {migration_name}")


async def run_migrations() -> None:
    """Run the migrations."""
    await wait_for_live()

    if not await check_db_migrations():
        print("Migration table doesn't yet exist - creating")
        await create_db_migrations()

    code_migrations = get_code_migrations()
    print(f"Code migrations: {list(code_migrations.keys())}")

    db_migrations = await get_db_migrations()
    print(f"DB migrations: {db_migrations}")

    needed = compute_needed_migrations(
        code_migrations=list(code_migrations.keys()),
        db_migrations=db_migrations,
    )
    print(f"Will run {needed}")

    for name in needed:
        await run_migration(name, code_migrations[name])


if __name__ == "__main__":
    asyncio.run(run_migrations())
