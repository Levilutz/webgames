def _verify_email_lowercase(email_address: str) -> None:
    """Throw exception if email is not lowercase."""
    if email_address != email_address.lower():
        raise Exception("Email address should be lowercase by now")
