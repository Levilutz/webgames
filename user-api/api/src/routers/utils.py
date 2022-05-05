from contextlib import contextmanager
from typing import Any, Dict, Iterator, List

from fastapi import HTTPException

from exceptions import InternalError, UserError


@contextmanager
def sanitize_excs(*args: List[Any], **kwargs: Dict[Any, Any]) -> Iterator[None]:
    """Context manager to sanitize exceptions."""
    try:
        yield
    except InternalError as e:
        print(f"INTERNAL ERROR: {str(e)}")  # TODO make this a log
        raise HTTPException(status_code=500, detail="Internal server error")
    except UserError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"UNHANDLED ERROR: {str(e)}")  # TODO make this a log
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        pass
