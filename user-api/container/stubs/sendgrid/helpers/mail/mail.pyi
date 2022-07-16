from typing import Any, Dict, List, Optional, Union

from .mail_settings import MailSettings


class Mail(object):
    mail_settings: MailSettings

    def __init__(
        self,
        from_email: Optional[str] = ...,
        to_emails: Union[List[str], str] = ...,
        subject: str = ...,
        plain_text_content: Optional[str] = ...,
        html_content: Optional[str] = ...,
        amp_html_content: Optional[str] = ...,
        global_substitutions: Optional[Dict[Any, Any]] = ...,
        is_multiple: bool = ...,
    ) -> None: ...
