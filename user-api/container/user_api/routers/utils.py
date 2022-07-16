from contextlib import contextmanager
from typing import Any, Dict, Iterator, List

from fastapi import HTTPException

from user_api.exceptions import (
    ClientError,
    InternalError,
    NotFoundError,
    VerifyFailedError,
)


@contextmanager
def sanitize_excs(*args: List[Any], **kwargs: Dict[Any, Any]) -> Iterator[None]:
    """Context manager to sanitize exceptions."""
    try:
        yield
    except VerifyFailedError as e:
        print(f"VERIFY FAILED ERROR ESCAPED: {str(e)}")  # TODO make this a log crit
        raise HTTPException(status_code=500)
    except InternalError as e:
        print(f"INTERNAL ERROR: {str(e)}")  # TODO make this a log error
        raise HTTPException(status_code=500)
    except ClientError as e:
        print(f"CLIENT ERROR: {str(e)}")  # TODO make this a log debug
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundError as e:
        print(f"NOT FOUND ERROR: {str(e)}")  # TODO make this a log debug
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"UNHANDLED ERROR: {str(e)}")  # TODO make this a log error/crit?
        raise HTTPException(status_code=500)
    finally:
        pass
