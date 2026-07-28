"""
Sentinel AI — Reusable pagination helpers.

Usage in a route:
    from backend.services.shared.pagination import PaginationParams, paginate

    @router.get("/items", response_model=PaginatedResponse[ItemSchema])
    async def list_items(pagination: PaginationParams = Depends()):
        ...
"""

from typing import Generic, TypeVar, Sequence
from pydantic import BaseModel, Field
from fastapi import Query
from starlette.responses import Response

T = TypeVar("T")


class PaginationParams:
    """Dependency-injectable pagination parameters."""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number (1-indexed)"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.page_size = page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Standardized paginated response envelope."""

    items: Sequence[T]
    total: int
    page: int
    page_size: int
    total_pages: int


def paginate(
    items: Sequence[T],
    total: int,
    params: PaginationParams,
    response: Response,
) -> PaginatedResponse[T]:
    """Build a PaginatedResponse and set X-Total-Count header."""
    total_pages = max(1, (total + params.page_size - 1) // params.page_size)
    response.headers["X-Total-Count"] = str(total)
    return PaginatedResponse(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=total_pages,
    )
