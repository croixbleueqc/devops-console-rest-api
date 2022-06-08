import secrets
from typing import Any, Dict

from pydantic import BaseSettings, EmailStr


class Environment(BaseSettings):
    API_V1_STR = "/api/v1"
    HOOKS_API_STR = "/bitbucketcloud/hooks/repo"
    SECRET_KEY = secrets.token_urlsafe(32)
    ACCESS_TOKEN_TTL: int = 60 * 24 * 7  # 7 days

    ENVIRONMENT: str = "development"

    USERNAME: EmailStr | None = None
    PASSWORD: str | None = None

    MOCK_USERS = {
        "croix_bleue": {
            "id": 0,
            "username": "croix_bleue",
            "email": "cb@qc.croixbleue.ca",
            "full_name": "Croix Bleue",
            "password": "password",
        },
        "tom": {
            "id": 1,
            "username": "tom",
            "email": "tom@superacteur.com",
            "full_name": "The Real Tom Cruise",
            "password": "TomCruiseIsTheBest",
        },
    }

    class Config:
        env_file = None


environment = Environment()
