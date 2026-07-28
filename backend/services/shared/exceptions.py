"""
Sentinel AI — RFC 7807 Problem+JSON error responses.
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class SentinelException(HTTPException):
    """Base exception with RFC 7807 fields."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_type: str = "about:blank",
        title: str | None = None,
        instance: str | None = None,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_type = error_type
        self.title = title or detail
        self.instance = instance


class NotFoundError(SentinelException):
    def __init__(self, entity: str, entity_id: str):
        super().__init__(
            status_code=404,
            detail=f"{entity} with id '{entity_id}' not found.",
            error_type="sentinel:not-found",
            title=f"{entity} Not Found",
        )


class ConflictError(SentinelException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=409,
            detail=detail,
            error_type="sentinel:conflict",
            title="Conflict",
        )


class ForbiddenError(SentinelException):
    def __init__(self, detail: str = "You do not have permission to perform this action."):
        super().__init__(
            status_code=403,
            detail=detail,
            error_type="sentinel:forbidden",
            title="Forbidden",
        )


class UnauthorizedError(SentinelException):
    def __init__(self, detail: str = "Invalid or expired credentials."):
        super().__init__(
            status_code=401,
            detail=detail,
            error_type="sentinel:unauthorized",
            title="Unauthorized",
        )


class BadRequestError(SentinelException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=400,
            detail=detail,
            error_type="sentinel:bad-request",
            title="Bad Request",
        )


class InvalidStateTransitionError(SentinelException):
    """Raised when an incident state machine transition is invalid."""

    def __init__(self, current_status: str, attempted_action: str):
        super().__init__(
            status_code=409,
            detail=f"Cannot '{attempted_action}' an incident with status '{current_status}'.",
            error_type="sentinel:invalid-state-transition",
            title="Invalid State Transition",
        )


# ── Global exception handler (register on FastAPI app) ──────────
async def sentinel_exception_handler(request: Request, exc: SentinelException) -> JSONResponse:
    """Return RFC 7807 problem+json for all SentinelException subclasses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": exc.error_type,
            "title": exc.title,
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": exc.instance or str(request.url),
        },
        media_type="application/problem+json",
    )
