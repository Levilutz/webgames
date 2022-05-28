import os
from typing import Any

import psycopg


AsyncConnection = psycopg.AsyncConnection[Any]


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
