from datetime import date, datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskStatusEnum(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"


class TaskPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200, json_schema_extra={"example": "Build resume parser"})
    description: Optional[str] = Field(None, max_length=2000, json_schema_extra={"example": "Implement the resume parsing pipeline"})
    project_id: int = Field(..., gt=0, json_schema_extra={"example": 1})
    assignee_id: Optional[int] = Field(None, gt=0, json_schema_extra={"example": 1})
    status: TaskStatusEnum = Field(default=TaskStatusEnum.TODO, json_schema_extra={"example": "todo"})
    priority: TaskPriorityEnum = Field(default=TaskPriorityEnum.MEDIUM, json_schema_extra={"example": "high"})
    due_date: Optional[date] = Field(None, json_schema_extra={"example": "2026-09-30"})

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Task title cannot be empty or whitespace")
        return cleaned


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=200, json_schema_extra={"example": "Updated title"})
    description: Optional[str] = Field(None, max_length=2000, json_schema_extra={"example": "Updated task description"})
    assignee_id: Optional[int] = Field(None, gt=0, json_schema_extra={"example": 2})
    priority: Optional[TaskPriorityEnum] = Field(None, json_schema_extra={"example": "high"})
    due_date: Optional[date] = Field(None, json_schema_extra={"example": "2026-10-15"})
    status: Optional[TaskStatusEnum] = Field(None, json_schema_extra={"example": "in-progress"})

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            if not cleaned:
                raise ValueError("Task title cannot be empty or whitespace")
            return cleaned
        return v


class TaskStatusUpdate(BaseModel):
    status: TaskStatusEnum = Field(..., json_schema_extra={"example": "in-progress"})


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatusEnum
    priority: TaskPriorityEnum
    project_id: int
    assignee_id: Optional[int] = None
    due_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
