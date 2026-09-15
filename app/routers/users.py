from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import (
    ResponseEnvelope, PaginatedData,
    RESPONSES_404_USER, RESPONSES_409_EMAIL, RESPONSES_422, RESPONSES_500
)
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService
from app.utils.pagination import build_paginated_response

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.post(
    "",
    response_model=ResponseEnvelope[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Registers a new user account with validated credentials and hashed password.",
    responses={
        409: RESPONSES_409_EMAIL,
        422: RESPONSES_422,
        500: RESPONSES_500
    }
)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    user = UserService.create_user(db, user_in)
    return ResponseEnvelope(data=UserResponse.model_validate(user))


@router.get(
    "",
    response_model=ResponseEnvelope[PaginatedData[UserResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get paginated users",
    description="Retrieves users with pagination and optional search filter.",
    responses={
        422: RESPONSES_422,
        500: RESPONSES_500
    }
)
def get_users(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term for name or email"),
    db: Session = Depends(get_db)
):
    items, total = UserService.get_users(db, page=page, page_size=page_size, search=search)
    user_responses = [UserResponse.model_validate(u) for u in items]
    paginated = build_paginated_response(user_responses, total, page, page_size)
    return ResponseEnvelope(data=paginated)


@router.get(
    "/{user_id}",
    response_model=ResponseEnvelope[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
    description="Retrieves detailed information for a specific user.",
    responses={
        404: RESPONSES_404_USER,
        422: RESPONSES_422,
        500: RESPONSES_500
    }
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = UserService.get_user_by_id(db, user_id)
    return ResponseEnvelope(data=UserResponse.model_validate(user))


@router.patch(
    "/{user_id}",
    response_model=ResponseEnvelope[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Update user details",
    description="Partially updates an existing user's attributes (name, email, password).",
    responses={
        404: RESPONSES_404_USER,
        409: RESPONSES_409_EMAIL,
        422: RESPONSES_422,
        500: RESPONSES_500
    }
)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db)
):
    user = UserService.update_user(db, user_id, user_in)
    return ResponseEnvelope(data=UserResponse.model_validate(user))


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Deletes a user account by ID.",
    responses={
        404: RESPONSES_404_USER,
        500: RESPONSES_500
    }
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    UserService.delete_user(db, user_id)
    return None
