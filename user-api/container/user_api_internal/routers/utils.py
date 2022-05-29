from contextlib import contextmanager
from typing import Any, Dict, Iterator, List

from fastapi import HTTPException

from user_api_internal.exceptions import InternalError, UserError


@contextmanager
def sanitize_excs(*args: List[Any], **kwargs: Dict[Any, Any]) -> Iterator[None]:
    """Context manager to sanitize exceptions."""
    try:
        yield
    except InternalError as e:
        print(f"INTERNAL ERROR: {str(e)}")  # TODO make this a log error
        raise HTTPException(status_code=500, detail="Internal server error")
    except UserError as e:
        print(f"USER ERROR: {str(e)}")  # TODO make this a log debug
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"UNHANDLED ERROR: {str(e)}")  # TODO make this a log error
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        pass
