class ClientError(Exception):
    """Exceptions caused by the caller's error."""

    pass


class InternalError(Exception):
    """Exceptions caused by an internal error."""

    pass


class NotFoundError(Exception):
    """Exceptions caused by access to non-existent resources."""

    pass
