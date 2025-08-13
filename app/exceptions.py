"""
Exception handlers and middleware for the AI Avatar Video application.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger("ai-avatar-video")

def add_exception_handlers(app: FastAPI) -> None:
    """Add exception handlers to the FastAPI application."""
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions with structured response."""
        logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "status_code": exc.status_code,
                "message": exc.detail,
                "path": request.url.path,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors with detailed error messages."""
        errors = exc.errors()
        error_messages = []
        
        for error in errors:
            error_messages.append({
                "field": ".".join([str(loc) for loc in error["loc"]]),
                "message": error["msg"],
                "type": error["type"],
            })
        
        logger.warning(f"Validation Error: {error_messages}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": True,
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "Validation error",
                "path": request.url.path,
                "errors": error_messages,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions with error logging."""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": True,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Internal server error",
                "path": request.url.path,
                "detail": str(exc) if request.app.debug else "An unexpected error occurred",
            },
        )
