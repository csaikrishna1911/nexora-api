from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.project import Project
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatusUpdate, TaskStatusEnum, TaskPriorityEnum
from app.exceptions.handlers import NotFoundException
from app.utils.pagination import get_pagination_params


class TaskService:
    @staticmethod
    def create_task(db: Session, task_in: TaskCreate) -> Task:
        # Check project existence
        project = db.query(Project).filter(Project.id == task_in.project_id).first()
        if not project:
            raise NotFoundException(
                f"Project with ID {task_in.project_id} was not found",
                code="PROJECT_NOT_FOUND"
            )

        # Check assignee existence if provided
        if task_in.assignee_id is not None:
            assignee = db.query(User).filter(User.id == task_in.assignee_id).first()
            if not assignee:
                raise NotFoundException(
                    f"User with ID {task_in.assignee_id} specified as assignee was not found",
                    code="ASSIGNEE_NOT_FOUND"
                )

        status_val = task_in.status.value if isinstance(task_in.status, TaskStatusEnum) else task_in.status
        priority_val = task_in.priority.value if isinstance(task_in.priority, TaskPriorityEnum) else task_in.priority

        task = Task(
            title=task_in.title,
            description=task_in.description,
            status=status_val,
            priority=priority_val,
            project_id=task_in.project_id,
            assignee_id=task_in.assignee_id,
            due_date=task_in.due_date,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def get_tasks(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        project_id: Optional[int] = None,
        assignee_id: Optional[int] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None,
        sort: Optional[str] = "created_at"
    ) -> Tuple[List[Task], int]:
        query = db.query(Task)

        if project_id is not None:
            query = query.filter(Task.project_id == project_id)

        if assignee_id is not None:
            query = query.filter(Task.assignee_id == assignee_id)

        if status and status.strip():
            query = query.filter(Task.status == status.strip().lower())

        if priority and priority.strip():
            query = query.filter(Task.priority == priority.strip().lower())

        if search and search.strip():
            term = f"%{search.strip()}%"
            query = query.filter(or_(Task.title.ilike(term), Task.description.ilike(term)))

        # Sorting logic
        if sort:
            sort_lower = sort.lower().strip()
            if sort_lower in ["created_at", "+created_at", "asc"]:
                query = query.order_by(Task.created_at.asc())
            elif sort_lower in ["-created_at", "desc"]:
                query = query.order_by(Task.created_at.desc())
            elif sort_lower in ["due_date", "+due_date"]:
                query = query.order_by(Task.due_date.asc().nulls_last())
            elif sort_lower in ["-due_date"]:
                query = query.order_by(Task.due_date.desc().nulls_last())
            elif sort_lower in ["title", "+title"]:
                query = query.order_by(Task.title.asc())
            elif sort_lower in ["-title"]:
                query = query.order_by(Task.title.desc())
            else:
                query = query.order_by(Task.id.desc())
        else:
            query = query.order_by(Task.id.desc())

        total = query.count()
        offset, limit = get_pagination_params(page, page_size)
        items = query.offset(offset).limit(limit).all()

        return items, total

    @staticmethod
    def get_task_by_id(db: Session, task_id: int) -> Task:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise NotFoundException(
                f"Task with ID {task_id} was not found",
                code="TASK_NOT_FOUND"
            )
        return task

    @staticmethod
    def update_task(db: Session, task_id: int, task_in: TaskUpdate) -> Task:
        task = TaskService.get_task_by_id(db, task_id)

        if task_in.assignee_id is not None:
            assignee = db.query(User).filter(User.id == task_in.assignee_id).first()
            if not assignee:
                raise NotFoundException(
                    f"User with ID {task_in.assignee_id} specified as assignee was not found",
                    code="ASSIGNEE_NOT_FOUND"
                )
            task.assignee_id = task_in.assignee_id

        if task_in.title is not None:
            task.title = task_in.title
        if task_in.description is not None:
            task.description = task_in.description
        if task_in.status is not None:
            task.status = task_in.status.value if isinstance(task_in.status, TaskStatusEnum) else task_in.status
        if task_in.priority is not None:
            task.priority = task_in.priority.value if isinstance(task_in.priority, TaskPriorityEnum) else task_in.priority
        if task_in.due_date is not None:
            task.due_date = task_in.due_date

        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def update_task_status(db: Session, task_id: int, status_in: TaskStatusUpdate) -> Task:
        task = TaskService.get_task_by_id(db, task_id)
        status_val = status_in.status.value if isinstance(status_in.status, TaskStatusEnum) else status_in.status

        task.status = status_val
        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete_task(db: Session, task_id: int) -> None:
        task = TaskService.get_task_by_id(db, task_id)
        db.delete(task)
        db.commit()
