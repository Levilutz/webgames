from typing import Any, Dict, Optional, Protocol, Union

from .helpers.mail import Mail


class _MessageResponse(Protocol):
    status_code: int


class SendGridAPIClient(object):
    def __init__(
        self,
        api_key: str,
        host: str = ...,
        impersonate_subuser: Optional[str] = ...,
    ) -> None: ...

    def send(
        self,
        message: Union[Dict[Any, Any], Mail],
    ) -> _MessageResponse: ...
