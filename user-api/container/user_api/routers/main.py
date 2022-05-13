import asyncio
from typing import Any, Dict

from fastapi import FastAPI
from psycopg.types.json import set_json_dumps, set_json_loads
import orjson

from user_api import config
from user_api.internal.users import clean_sessions_loop
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


@app.get("/")
def root() -> Dict[Any, Any]:
    """Root url."""
    return {"message": "Hello World"}
