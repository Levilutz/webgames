import os
from typing import Optional, TypeVar, Type


T = TypeVar("T")

TEST_MODE = os.getenv("TEST_MODE")


def _get_env(name: str, required: bool = False) -> Optional[str]:
    """Retrieve an environment variable.

    Params:
        name - the name of the environment variable
        required - whether to err if the variable doesn't exist.

    Returns: The env var's contents as a string
    """
    value = os.getenv(name)
    if required and not value:
        if TEST_MODE:
            return ""
        else:
            raise Exception(f"Required env var not set: {name}")
    return value


def _get_env_cast(name: str, cast: Type[T]) -> T:
    """Retrieve a required environment variable and cast it.

    Params:
        name - the name of the environment variable
        cast - a Callable & Type to pass the variable through

    Returns: The env var's contents, cast as requested
    """
    value = _get_env(name, required=True)
    try:
        return cast(value)  # type: ignore
    except ValueError as e:
        raise Exception(
            f"Cannot cast env var to type '{cast}' - {name}: {value} - {str(e)}"
        )


EXPECTED_PREFIX = _get_env("EXPECTED_PREFIX") or ""
DB_USER = _get_env("DB_USER", required=True)
DB_PASS = _get_env("DB_PASS", required=True)
DB_ADDRESS = _get_env("DB_ADDRESS", required=True)
DB_PORT = _get_env("DB_PORT", required=True)
DB_NAME = _get_env("DB_NAME", required=True)
