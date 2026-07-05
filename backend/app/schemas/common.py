from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class PaginationMeta(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    total: int
    total_pages: int


class ResponseMeta(BaseModel):
    request_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[list[ErrorDetail]] = None


class APIResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    error: Optional[ErrorResponse] = None
    meta: ResponseMeta = Field(default_factory=ResponseMeta)


class PaginatedResponse(APIResponse):
    data: Optional[list[Any]] = None
    pagination: Optional[PaginationMeta] = None
