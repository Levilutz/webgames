import asyncio
from typing import Any

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from psycopg.types.json import set_json_dumps, set_json_loads
import orjson

from user_api import config
from user_api.internal.auth import clean_db_loop
from user_api.routers import auth


app = FastAPI(root_path=config.EXPECTED_PREFIX)


def json_dumps(data: Any) -> str:
    return orjson.dumps(data).decode("utf-8")


set_json_dumps(json_dumps)
set_json_loads(orjson.loads)

# Add routers
app.include_router(auth.router)


@app.on_event("startup")
async def app_startup() -> None:
    """Verify config, start background tasks."""
    # Validate env vars set
    if any([var is None for var in config.REQUIRED_ENV_FOR_DEPLOY]):
        raise Exception(f"Missing required env vars: {config.REQUIRED_ENV_FOR_DEPLOY}")

    # Start cleaning stuff up
    asyncio.create_task(clean_db_loop())


@app.get("/ping", response_class=PlainTextResponse)
def ping() -> str:
    """Ping pong."""
    return "pong"
