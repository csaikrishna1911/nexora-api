from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.database import engine
from app.models.base import Base
from app.exceptions.handlers import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
)
from app.schemas.common import ErrorEnvelope
from app.routers import users_router, projects_router, tasks_router, dashboard_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database tables exist
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="A production-ready REST API for teams, projects, and task execution.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS Configuration
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Include Health Check
@app.get(
    "/health",
    tags=["Health"],
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    description="Returns service availability and operational health status."
)
def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME
    }

# Include API Routers
app.include_router(users_router)
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(dashboard_router)


def custom_openapi():
    """Generates custom OpenAPI schema accurately reflecting centralized ErrorEnvelope error structures."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Ensure ErrorEnvelope is in components/schemas
    if "ErrorEnvelope" not in openapi_schema.get("components", {}).get("schemas", {}):
        openapi_schema.setdefault("components", {}).setdefault("schemas", {})["ErrorEnvelope"] = ErrorEnvelope.model_json_schema()

    # Standardize all 422 responses across OpenAPI routes to use ErrorEnvelope
    for path, methods in openapi_schema.get("paths", {}).items():
        for method, details in methods.items():
            responses = details.get("responses", {})
            if "422" in responses:
                responses["422"]["description"] = "Validation Error"
                responses["422"]["content"] = {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorEnvelope"},
                        "example": {
                            "success": False,
                            "error": {
                                "code": "VALIDATION_ERROR",
                                "message": "Request validation failed",
                                "details": [
                                    {
                                        "field": "email",
                                        "message": "value is not a valid email address",
                                        "type": "value_error"
                                    }
                                ]
                            }
                        }
                    }
                }

    # Clean up default unused FastAPI validation schemas
    schemas = openapi_schema.get("components", {}).get("schemas", {})
    schemas.pop("HTTPValidationError", None)
    schemas.pop("ValidationError", None)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
