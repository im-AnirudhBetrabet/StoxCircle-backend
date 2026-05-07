from app.core.exceptions import AppException
from fastapi import status
from app.utils.logger import sys_logger

def handle_response(res):
    if hasattr(res, "error") and res.error:
        sys_logger.error(f"Unable to process request due to an unexpected error: {res.error}")
        raise AppException(status.HTTP_400_BAD_REQUEST, str(res.error))
    return res.data