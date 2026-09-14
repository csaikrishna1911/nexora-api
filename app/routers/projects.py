from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import ResponseEnvelope, PaginatedData
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetailResponse, TaskStats
from app.services.project_service import ProjectService
from app.utils.pagination import build_paginated_response

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])


@router.post(
    "",
    response_model=ResponseEnvelope[ProjectResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a project",
    description="Creates a new project owned by a valid user."
)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db)
):
    project = ProjectService.create_project(db, project_in)
    return ResponseEnvelope(data=ProjectResponse.model_validate(project))


@router.get(
    "",
    response_model=ResponseEnvelope[PaginatedData[ProjectResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get paginated projects",
    description="Retrieves projects with filtering, searching, sorting, and pagination."
)
def get_projects(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search name or description"),
    owner_id: Optional[int] = Query(None, description="Filter by owner user ID"),
    sort: Optional[str] = Query("created_at", description="Sort field (created_at, -created_at, name, -name)"),
    db: Session = Depends(get_db)
):
    items, total = ProjectService.get_projects(
        db, page=page, page_size=page_size, search=search, owner_id=owner_id, sort=sort
    )
    project_responses = [ProjectResponse.model_validate(p) for p in items]
    paginated = build_paginated_response(project_responses, total, page, page_size)
    return ResponseEnvelope(data=paginated)


@router.get(
    "/{project_id}",
    response_model=ResponseEnvelope[ProjectDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Get project by ID",
    description="Retrieves a project by ID along with its task statistics breakdown."
)
def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = ProjectService.get_project_by_id(db, project_id)
    stats = ProjectService.get_project_stats(db, project_id)
    
    response_data = ProjectDetailResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
        created_at=project.created_at,
        updated_at=project.updated_at,
        task_stats=TaskStats(**stats)
    )
    return ResponseEnvelope(data=response_data)


@router.patch(
    "/{project_id}",
    response_model=ResponseEnvelope[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="Update project",
    description="Updates project name or description."
)
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db)
):
    project = ProjectService.update_project(db, project_id, project_in)
    return ResponseEnvelope(data=ProjectResponse.model_validate(project))


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
    description="Deletes a project and all associated tasks."
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    ProjectService.delete_project(db, project_id)
    return None
