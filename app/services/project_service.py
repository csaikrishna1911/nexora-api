from datetime import datetime
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.exceptions.handlers import NotFoundException
from app.utils.pagination import get_pagination_params


class ProjectService:
    @staticmethod
    def create_project(db: Session, project_in: ProjectCreate) -> Project:
        # Check owner exists
        owner = db.query(User).filter(User.id == project_in.owner_id).first()
        if not owner:
            raise NotFoundException(
                f"User with ID {project_in.owner_id} specified as owner was not found",
                code="OWNER_NOT_FOUND"
            )

        project = Project(
            name=project_in.name,
            description=project_in.description,
            owner_id=project_in.owner_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get_projects(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        owner_id: Optional[int] = None,
        sort: Optional[str] = "created_at"
    ) -> Tuple[List[Project], int]:
        query = db.query(Project)

        if owner_id is not None:
            query = query.filter(Project.owner_id == owner_id)

        if search and search.strip():
            term = f"%{search.strip()}%"
            query = query.filter(or_(Project.name.ilike(term), Project.description.ilike(term)))

        # Sorting logic
        if sort:
            sort_lower = sort.lower().strip()
            if sort_lower in ["created_at", "+created_at", "asc"]:
                query = query.order_by(Project.created_at.asc())
            elif sort_lower in ["-created_at", "desc"]:
                query = query.order_by(Project.created_at.desc())
            elif sort_lower in ["name", "+name"]:
                query = query.order_by(Project.name.asc())
            elif sort_lower in ["-name"]:
                query = query.order_by(Project.name.desc())
            else:
                query = query.order_by(Project.id.desc())
        else:
            query = query.order_by(Project.id.desc())

        total = query.count()
        offset, limit = get_pagination_params(page, page_size)
        items = query.offset(offset).limit(limit).all()

        return items, total

    @staticmethod
    def get_project_by_id(db: Session, project_id: int) -> Project:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundException(
                f"Project with ID {project_id} was not found",
                code="PROJECT_NOT_FOUND"
            )
        return project

    @staticmethod
    def get_project_stats(db: Session, project_id: int) -> Dict[str, int]:
        tasks = db.query(Task.status, func.count(Task.id)).filter(Task.project_id == project_id).group_by(Task.status).all()
        stats = {
            "total_tasks": 0,
            "todo": 0,
            "in_progress": 0,
            "done": 0
        }
        for status_val, count in tasks:
            stats["total_tasks"] += count
            if status_val == "todo":
                stats["todo"] = count
            elif status_val == "in-progress":
                stats["in_progress"] = count
            elif status_val == "done":
                stats["done"] = count

        return stats

    @staticmethod
    def update_project(db: Session, project_id: int, project_in: ProjectUpdate) -> Project:
        project = ProjectService.get_project_by_id(db, project_id)

        if project_in.name is not None:
            project.name = project_in.name
        if project_in.description is not None:
            project.description = project_in.description

        project.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete_project(db: Session, project_id: int) -> None:
        project = ProjectService.get_project_by_id(db, project_id)
        db.delete(project)
        db.commit()
