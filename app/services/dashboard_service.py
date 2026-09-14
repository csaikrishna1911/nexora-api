from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.schemas.dashboard import DashboardSummary, TasksByStatus, TasksByPriority


class DashboardService:
    @staticmethod
    def get_summary(db: Session) -> DashboardSummary:
        user_count = db.query(func.count(User.id)).scalar() or 0
        project_count = db.query(func.count(Project.id)).scalar() or 0
        task_count = db.query(func.count(Task.id)).scalar() or 0

        status_counts = db.query(Task.status, func.count(Task.id)).group_by(Task.status).all()
        by_status = {"todo": 0, "in-progress": 0, "done": 0}
        for st, count in status_counts:
            if st in by_status:
                by_status[st] = count

        priority_counts = db.query(Task.priority, func.count(Task.id)).group_by(Task.priority).all()
        by_priority = {"low": 0, "medium": 0, "high": 0}
        for pr, count in priority_counts:
            if pr in by_priority:
                by_priority[pr] = count

        return DashboardSummary(
            users=user_count,
            projects=project_count,
            tasks=task_count,
            tasks_by_status=TasksByStatus(
                todo=by_status["todo"],
                in_progress=by_status["in-progress"],
                done=by_status["done"]
            ),
            tasks_by_priority=TasksByPriority(
                low=by_priority["low"],
                medium=by_priority["medium"],
                high=by_priority["high"]
            )
        )
