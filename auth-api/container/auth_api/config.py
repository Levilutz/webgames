import os
from typing import TypeVar, Type


T = TypeVar("T")


def _get_env_required(name: str) -> str:
    """Retrieve a required environment variable."""
    value = os.getenv(name)
    if not value:
        raise Exception(f"Required env var not set: {name}")
    return value


def _get_env_cast(name: str, cast: Type[T]) -> T:
    """Retrieve a required environment variable and cast it.

    Params:
        name - the name of the environment variable
        cast - a Callable & Type to pass the variable through

    Returns: The env var's contents, cast as requested
    """
    value = _get_env_required(name)
    try:
        return cast(value)  # type: ignore
    except ValueError as e:
        raise Exception(
            f"Cannot cast env var to type '{cast}' - {name}: {value} - {str(e)}"
        )


def _url_clean(url: str) -> str:
    """Remove trailing slash from URL, ensure http:// or https://."""
    url = url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        raise Exception(f"URL '{url}' doesn't start with http:// or https://")
    if url[-1] == "/":
        url = url[:-1]
    return url


EXPECTED_PREFIX = os.getenv("EXPECTED_PREFIX") or ""
USER_API_URL = _url_clean(_get_env_required("USER_API_URL"))
