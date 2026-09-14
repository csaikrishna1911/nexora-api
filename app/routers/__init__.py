from app.routers.users import router as users_router
from app.routers.projects import router as projects_router
from app.routers.tasks import router as tasks_router
from app.routers.dashboard import router as dashboard_router

__all__ = ["users_router", "projects_router", "tasks_router", "dashboard_router"]
