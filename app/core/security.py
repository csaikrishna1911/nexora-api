import re
import bcrypt
from app.exceptions.handlers import ValidationException


def hash_password(password: str) -> str:
    """Securely hash password using bcrypt."""
    # Truncate to 72 bytes per bcrypt standard limit
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against stored bcrypt hash."""
    pwd_bytes = plain_password.encode('utf-8')[:72]
    return bcrypt.checkpw(pwd_bytes, hashed_password.encode('utf-8'))


def validate_password_strength(password: str) -> None:
    """
    Validate password requirements:
    - Min 8 characters
    - Max 128 characters
    - Must contain at least one letter and one number
    """
    if len(password) < 8:
        raise ValidationException("Password must be at least 8 characters long")
    if len(password) > 128:
        raise ValidationException("Password must not exceed 128 characters")
    if not re.search(r"[A-Za-z]", password):
        raise ValidationException("Password must contain at least one letter")
    if not re.search(r"\d", password):
        raise ValidationException("Password must contain at least one number")
