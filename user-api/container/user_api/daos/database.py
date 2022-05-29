from typing import Any

import psycopg

from user_api import config


AsyncConnection = psycopg.AsyncConnection[Any]


async def get_db_connection() -> psycopg.AsyncConnection[Any]:
    """Get a new db connection."""
    conn = await psycopg.AsyncConnection.connect(
        user=config.DB_USER,
        password=config.DB_PASS,
        host=config.DB_ADDRESS,
        port=config.DB_PORT,
        dbname=config.DB_NAME,
    )

    return conn
