from collections import UserDict
import secrets

from devops_console.config import Config
from devops_sccs.cache import Cache
from pydantic import BaseSettings, EmailStr


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


class ExternalConfig(UserDict):
    def __init__(self, config: dict):
        super().__init__(config)
        self.parse_config(config)

    def parse_config(self, config: dict):
        self.cd_environments = config["continous_deployment"]["environments"]
        self.cd_branches_accepted = [env["branch"] for env in self.cd_environments]
        self.cd_pullrequest_tag = config["continous_deployment"]["pullrequest"]["tag"]
        self.cd_versions_available = config["continous_deployment"]["pipeline"][
            "versions_available"
        ]
        self.watcher_user = config["watcher"]["user"]
        self.watcher_pwd = config["watcher"]["pwd"]


external_config: ExternalConfig = ExternalConfig({})
