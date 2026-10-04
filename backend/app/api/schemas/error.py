"""Error response schemas."""

from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    """Standard error response."""

    success: bool = False
    error: str
    detail: Optional[str] = None