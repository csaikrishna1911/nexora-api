from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import (
    ResponseEnvelope, PaginatedData,
    RESPONSES_404_TASK, RESPONSES_404_PROJECT, RESPONSES_422, RESPONSES_500
)
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskStatusUpdate, TaskResponse, TaskStatusEnum, TaskPriorityEnum
)
from app.services.task_service import TaskService
from app.utils.pagination import build_paginated_response

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=ResponseEnvelope[TaskResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
    description="Creates a task within a specified project, optionally assigning to a user.",
    responses={
        404: RESPONSES_404_PROJECT,
        422: RESPONSES_422,
        500: RESPONSES_500
    }
)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db)
):
    task = TaskService.create_task(db, task_in)
    return ResponseEnvelope(data=TaskResponse.model_validate(task))


@router.get(
    "",
    response_model=ResponseEnvelope[PaginatedData[TaskResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get paginated tasks",
    description="Retrieves tasks with filtering (project, assignee, status, priority), search, and pagination.",
    responses={
        422: RESPONSES_422,
        500: RESPONSES_500
    }
)
def get_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee user ID"),
    status: Optional[TaskStatusEnum] = Query(None, description="Filter by status (todo, in-progress, done)"),
    priority: Optional[TaskPriorityEnum] = Query(None, description="Filter by priority (low, medium, high)"),
    search: Optional[str] = Query(None, description="Search term for title or description"),
    sort: Optional[str] = Query("created_at", description="Sort field (created_at, -created_at, due_date, -due_date, title)"),
    db: Session = Depends(get_db)
):
    status_str = status.value if status else None
    priority_str = priority.value if priority else None

    items, total = TaskService.get_tasks(
        db,
        page=page,
        page_size=page_size,
        project_id=project_id,
        assignee_id=assignee_id,
        status=status_str,
        priority=priority_str,
        search=search,
        sort=sort
    )
    task_responses = [TaskResponse.model_validate(t) for t in items]
    paginated = build_paginated_response(task_responses, total, page, page_size)
    return ResponseEnvelope(data=paginated)


@router.get(
    "/{task_id}",
    response_model=ResponseEnvelope[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="Get task by ID",
    description="Retrieves detailed information for a specific task.",
    responses={
        404: RESPONSES_404_TASK,
        422: RESPONSES_422,
        500: RESPONSES_500
    }
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    task = TaskService.get_task_by_id(db, task_id)
    return ResponseEnvelope(data=TaskResponse.model_validate(task))


@router.patch(
    "/{task_id}",
    response_model=ResponseEnvelope[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="Update task details",
    description="Partially updates task fields (title, description, assignee_id, priority, due_date, status).",
    responses={
        404: RESPONSES_404_TASK,
        422: RESPONSES_422,
        500: RESPONSES_500
    }
)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db)
):
    task = TaskService.update_task(db, task_id, task_in)
    return ResponseEnvelope(data=TaskResponse.model_validate(task))


@router.patch(
    "/{task_id}/status",
    response_model=ResponseEnvelope[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="Update task status",
    description="Updates only the execution status of a task (todo, in-progress, done).",
    responses={
        404: RESPONSES_404_TASK,
        422: RESPONSES_422,
        500: RESPONSES_500
    }
)
def update_task_status(
    task_id: int,
    status_in: TaskStatusUpdate,
    db: Session = Depends(get_db)
):
    task = TaskService.update_task_status(db, task_id, status_in)
    return ResponseEnvelope(data=TaskResponse.model_validate(task))


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Deletes a task by ID.",
    responses={
        404: RESPONSES_404_TASK,
        500: RESPONSES_500
    }
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    TaskService.delete_task(db, task_id)
    return None
