from pydantic import BaseModel, ConfigDict, Field


class TasksByStatus(BaseModel):
    todo: int = 0
    in_progress: int = Field(0, serialization_alias="in-progress", validation_alias="in-progress")
    done: int = 0

    model_config = ConfigDict(populate_by_name=True)


class TasksByPriority(BaseModel):
    low: int = 0
    medium: int = 0
    high: int = 0


class DashboardSummary(BaseModel):
    users: int = 0
    projects: int = 0
    tasks: int = 0
    tasks_by_status: TasksByStatus
    tasks_by_priority: TasksByPriority
