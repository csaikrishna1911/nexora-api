from typing import Generic, List, TypeVar, Any, Optional
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
    code: str = Field(..., json_schema_extra={"example": "NOT_FOUND"})
    message: str = Field(..., json_schema_extra={"example": "Resource with specified ID was not found"})
    details: List[Any] = Field(default=[], json_schema_extra={"example": []})


class ErrorEnvelope(BaseModel):
    success: bool = False
    error: ErrorPayload


def error_response_spec(
    description: str,
    code: str,
    message: str,
    details: Optional[List[Any]] = None
) -> dict:
    """Helper to generate OpenAPI documentation spec for error responses."""
    return {
        "model": ErrorEnvelope,
        "description": description,
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": {
                        "code": code,
                        "message": message,
                        "details": details or []
                    }
                }
            }
        }
    }


# Standard reusable OpenAPI response specs
RESPONSES_400 = error_response_spec("Bad Request", "BAD_REQUEST", "Invalid request parameters")
RESPONSES_404_USER = error_response_spec("User Not Found", "USER_NOT_FOUND", "User with ID 12 was not found")
RESPONSES_404_PROJECT = error_response_spec("Project Not Found", "PROJECT_NOT_FOUND", "Project with ID 12 was not found")
RESPONSES_404_TASK = error_response_spec("Task Not Found", "TASK_NOT_FOUND", "Task with ID 12 was not found")
RESPONSES_404_OWNER = error_response_spec("Owner Not Found", "OWNER_NOT_FOUND", "User specified as owner was not found")
RESPONSES_404_ASSIGNEE = error_response_spec("Assignee Not Found", "ASSIGNEE_NOT_FOUND", "User specified as assignee was not found")
RESPONSES_409_EMAIL = error_response_spec("Conflict / Email Exists", "USER_EMAIL_EXISTS", "User with email 'sai@example.com' already exists")
RESPONSES_422 = error_response_spec(
    "Validation Error",
    "VALIDATION_ERROR",
    "Request validation failed",
    details=[{"field": "email", "message": "value is not a valid email address", "type": "value_error"}]
)
RESPONSES_500 = error_response_spec("Internal Server Error", "INTERNAL_SERVER_ERROR", "An unexpected internal server error occurred")
