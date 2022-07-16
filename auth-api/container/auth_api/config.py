import os


def _url_clean(url: str) -> str:
    """Remove trailing slash from URL, ensure http:// or https://."""
    url = url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        raise Exception(f"URL '{url}' doesn't start with http:// or https://")
    if url[-1] == "/":
        url = url[:-1]
    return url


# Env var config
EXPECTED_PREFIX = os.getenv("EXPECTED_PREFIX") or ""
USER_API_URL_DIRTY = os.getenv("USER_API_URL")


# Env vars required for a full deployment, checked in app_startup
REQUIRED_ENV_FOR_DEPLOY = [
    USER_API_URL_DIRTY,
]


# Computed config
USER_API_URL = None if USER_API_URL_DIRTY is None else _url_clean(USER_API_URL_DIRTY)
