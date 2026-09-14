from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskStats(BaseModel):
    total_tasks: int = 0
    todo: int = 0
    in_progress: int = Field(0, serialization_alias="in_progress")
    done: int = 0


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150, json_schema_extra={"example": "AI Resume Analyzer"})
    description: Optional[str] = Field(None, max_length=1000, json_schema_extra={"example": "An AI-powered resume analysis platform"})
    owner_id: int = Field(..., gt=0, json_schema_extra={"example": 1})

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Project name cannot be empty or whitespace")
        return cleaned


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150, json_schema_extra={"example": "Updated Resume Analyzer"})
    description: Optional[str] = Field(None, max_length=1000, json_schema_extra={"example": "Updated description"})

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            if not cleaned:
                raise ValueError("Project name cannot be empty or whitespace")
            return cleaned
        return v


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectDetailResponse(ProjectResponse):
    task_stats: TaskStats
