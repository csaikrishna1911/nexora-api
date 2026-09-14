from typing import Generic, List, TypeVar, Any
from pydantic import BaseModel, Field

DataType = TypeVar("DataType")


class PaginationMeta(BaseModel):
    page: int = Field(..., json_schema_extra={"example": 1}, ge=1)
    page_size: int = Field(..., json_schema_extra={"example": 10}, ge=1, le=100)
    total: int = Field(..., json_schema_extra={"example": 42}, ge=0)
    total_pages: int = Field(..., json_schema_extra={"example": 5}, ge=0)


class PaginatedData(BaseModel, Generic[DataType]):
    items: List[DataType]
    pagination: PaginationMeta


class ResponseEnvelope(BaseModel, Generic[DataType]):
    success: bool = True
    data: DataType


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: List[Any] = []


class ErrorEnvelope(BaseModel):
    success: bool = False
    error: ErrorPayload
