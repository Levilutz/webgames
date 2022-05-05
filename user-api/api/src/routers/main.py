import asyncio
from typing import Any, Dict

from fastapi import FastAPI
from psycopg.types.json import set_json_dumps, set_json_loads
import orjson

from internal import users

from routers import api_models
from routers.utils import sanitize_excs


app = FastAPI()


def json_dumps(data: Any) -> str:
    return orjson.dumps(data).decode("utf-8")


set_json_dumps(json_dumps)
set_json_loads(orjson.loads)


@app.on_event("startup")
async def app_startup() -> None:
    """Start background tasks."""
    asyncio.create_task(users.clean_sessions_loop())


@app.get("/")
def root() -> Dict[Any, Any]:
    """Root url."""
    return {"message": "Hello World"}


@app.get("/register")
async def register(
    register_request: api_models.RegisterRequest,
) -> api_models.SuccessResponse:
    """Register a new user."""
    with sanitize_excs():
        await users.register(
            username=register_request.username,
            password=register_request.password,
        )
    return api_models.success
