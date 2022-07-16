from typing import Any, Callable, Dict, Type, TypeVar

import requests

from auth_api.config import USER_API_URL
from auth_api.exceptions import ClientError, InternalError, NotFoundError


T = TypeVar("T")

# Which Errors to propagate expected status codes with
_handled_codes: Dict[int, Callable[[Any], Exception]] = {
    400: ClientError,
    404: NotFoundError,
    500: InternalError,
}


def _decode_json_safe(resp: requests.Response) -> Any:
    """Decode json data, raise InternalError if failure."""
    try:
        return resp.json()
    except Exception as e:
        raise InternalError(f"Failed to parse JSON for '{str(e)}' - {resp.text}")


def _request(method: str, path: str, body: Any = None, params: Any = None) -> Any:
    """Make a request to the user-api, handle bad status codes.

    This doesn't need headers, query string params, etc bc user-api currently doesn't
    have any endpoints making use of those.
    """
    # Prepare args
    if path and path[0] != "/":
        print("Path '{path}' doesn't have leading '/'")  # TODO replace with log warning
        path = "/" + path
    url = USER_API_URL + path

    # Make the request
    # Let exceptions propagate as unhandled
    resp = requests.request(method, url, json=body, params=params)

    # If 200, pass result up
    if resp.status_code == 200:
        return _decode_json_safe(resp) if resp.text else None

    # If 400/404/500, propagate the same exc onward (unless caller catches)
    elif resp.status_code in _handled_codes:
        detail = _decode_json_safe(resp).get("detail", "No Detail")
        MatchingError = _handled_codes[resp.status_code]
        raise MatchingError(detail)

    # Else, this is problematic so let it log err
    else:
        raise Exception(f"Unexpected response {resp.status_code} - {resp.text}")


def _request_shaped(output_obj: Type[T], method: str, path: str, body: Any = None) -> T:
    """Request to user-api, shape the output object."""
    # Ensure output_obj is valid
    if not hasattr(output_obj, "parse_obj"):
        raise Exception(f"Cannot parse into bad type '{type(output_obj)}'")

    # Get response
    resp_raw = _request(method=method, path=path, body=body)

    # Parse object
    # Let parsing exceptions propagate
    return output_obj.parse_obj(resp_raw)  # type: ignore
