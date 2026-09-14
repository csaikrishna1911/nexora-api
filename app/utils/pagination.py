import math
from typing import List, TypeVar, Tuple
from app.schemas.common import PaginationMeta, PaginatedData

T = TypeVar("T")


def get_pagination_params(page: int = 1, page_size: int = 10) -> Tuple[int, int]:
    """Ensure safe page and page_size constraints and return (offset, limit)."""
    safe_page = max(1, page)
    safe_page_size = max(1, min(100, page_size))
    offset = (safe_page - 1) * safe_page_size
    return offset, safe_page_size


def build_paginated_response(items: List[T], total: int, page: int, page_size: int) -> PaginatedData[T]:
    """Construct standard paginated data payload."""
    safe_page = max(1, page)
    safe_page_size = max(1, min(100, page_size))
    total_pages = math.ceil(total / safe_page_size) if total > 0 else 0

    meta = PaginationMeta(
        page=safe_page,
        page_size=safe_page_size,
        total=total,
        total_pages=total_pages
    )
    return PaginatedData(items=items, pagination=meta)
