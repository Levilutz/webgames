from typing import Any, Dict

from fastapi import FastAPI
from psycopg.types.json import set_json_dumps, set_json_loads
import orjson


app = FastAPI()


def json_dumps(data: Any) -> str:
    return orjson.dumps(data).decode("utf-8")


set_json_dumps(json_dumps)
set_json_loads(orjson.loads)


@app.get("/")
def root() -> Dict[Any, Any]:
    """Root url."""
    return {"message": "Hello World"}
