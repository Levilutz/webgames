from typing import Any, Optional

from .sandbox_mode import SandBoxMode


class MailSettings(object):
    def __init__(
        self,
        bcc_settings: Any = ...,
        bypass_bounce_management: Any = ...,
        bypass_list_management: Any = ...,
        bypass_spam_management: Any = ...,
        bypass_unsubscribe_management: Any = ...,
        footer_settings: Any = ...,
        sandbox_mode: Optional[SandBoxMode] = ...,
        spam_check: Any = ...,
    ) -> None: ...
