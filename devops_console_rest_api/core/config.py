import secrets

from pydantic import BaseSettings, EmailStr
from devops_sccs.cache import Cache


class Settings(BaseSettings):
    API_V1_STR = "/api/v1"
    HOOKS_API_STR = "/bitbucketcloud/hooks/repo"
    SECRET_KEY = secrets.token_urlsafe(32)
    ACCESS_TOKEN_TTL: int = 60 * 24 * 7  # 7 days

    ENVIRONMENT: str

    SUPERUSER_USERNAME: EmailStr
    SUPERUSER_PASSWORD: str

    USERNAME: EmailStr
    PASSWORD: str

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
    INIT_CACHE = {}

    class Config:
        env_file = ".env"


settings = Settings()  # type: ignore

cache = Cache(settings.INIT_CACHE)
