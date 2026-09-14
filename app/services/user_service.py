from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password, validate_password_strength
from app.exceptions.handlers import NotFoundException, ConflictException
from app.utils.pagination import get_pagination_params


class UserService:
    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> User:
        # Check duplicate email
        existing = db.query(User).filter(User.email == user_in.email).first()
        if existing:
            raise ConflictException(
                f"User with email '{user_in.email}' already exists",
                code="USER_EMAIL_EXISTS"
            )

        # Validate password strength
        validate_password_strength(user_in.password)

        user = User(
            name=user_in.name,
            email=user_in.email,
            password_hash=hash_password(user_in.password),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_users(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None
    ) -> Tuple[List[User], int]:
        query = db.query(User)

        if search and search.strip():
            term = f"%{search.strip()}%"
            query = query.filter(or_(User.name.ilike(term), User.email.ilike(term)))

        total = query.count()
        offset, limit = get_pagination_params(page, page_size)
        items = query.order_by(User.id.asc()).offset(offset).limit(limit).all()

        return items, total

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException(
                f"User with ID {user_id} was not found",
                code="USER_NOT_FOUND"
            )
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, user_in: UserUpdate) -> User:
        user = UserService.get_user_by_id(db, user_id)

        if user_in.email is not None and user_in.email != user.email:
            existing = db.query(User).filter(User.email == user_in.email, User.id != user_id).first()
            if existing:
                raise ConflictException(
                    f"User with email '{user_in.email}' already exists",
                    code="USER_EMAIL_EXISTS"
                )
            user.email = user_in.email

        if user_in.name is not None:
            user.name = user_in.name

        if user_in.password is not None:
            validate_password_strength(user_in.password)
            user.password_hash = hash_password(user_in.password)

        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> None:
        user = UserService.get_user_by_id(db, user_id)
        db.delete(user)
        db.commit()
