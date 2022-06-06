from datetime import datetime, timedelta
from typing import Any
from passlib.context import CryptContext
from jose import jwt

from devops_console_rest_api.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str | Any, ttl: timedelta | None = None) -> str:
    if ttl:
        expire = datetime.utcnow() + ttl
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_TTL)
    jwt_input = {"exp": expire, "sub": str(subject)}

    return jwt.encode(jwt_input, settings.SECRET_KEY, algorithm=ALGORITHM)
