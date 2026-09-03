"""
Custom Exception Handlers

Defines custom exceptions and error handlers for the application.
"""

import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger(__name__)


class AstrologyCalculationError(Exception):
    """Raised when astrology calculations fail"""

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class InvalidBirthDataError(Exception):
    """Raised when birth data is invalid"""

    def __init__(self, message: str, field: str = None, value: any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)


async def astrology_calculation_error_handler(
    request: Request, exc: AstrologyCalculationError
):
    """Handle astrology calculation errors"""
    logger.error("Astrology calculation error", exc_info=(type(exc), exc, exc.__traceback__))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "ASTROLOGY_CALCULATION_ERROR",
                "message": "Astrology calculation failed",
                "details": {},
            }
        },
    )


async def invalid_birth_data_error_handler(request: Request, exc: InvalidBirthDataError):
    """Handle invalid birth data errors"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "INVALID_BIRTH_DATA",
                "message": exc.message,
                "field": exc.field,
                "value": exc.value,
            }
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": exc.errors(),
            }
        },
    )
