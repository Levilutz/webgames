import asyncio
from typing import Any

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from psycopg.types.json import set_json_dumps, set_json_loads
import orjson

from user_api import config
from user_api.internal.auth import clean_sessions_loop
from user_api.routers import users


app = FastAPI(root_path=config.EXPECTED_PREFIX)


def json_dumps(data: Any) -> str:
    return orjson.dumps(data).decode("utf-8")


set_json_dumps(json_dumps)
set_json_loads(orjson.loads)

# Add routers
app.include_router(users.router)


@app.on_event("startup")
async def app_startup() -> None:
    """Start background tasks."""
    asyncio.create_task(clean_sessions_loop())


@app.get("/ping", response_class=PlainTextResponse)
def root() -> str:
    """Ping pong."""
    return "pong"
