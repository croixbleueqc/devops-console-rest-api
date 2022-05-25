from collections import UserDict
import secrets
from typing import Any, Dict

from pydantic import BaseSettings, EmailStr
from devops_sccs.cache import ThreadsafeCache


class Settings(BaseSettings):
    API_V1_STR = "/api/v1"
    HOOKS_API_STR = "/bitbucketcloud/hooks/repo"
    SECRET_KEY = secrets.token_urlsafe(32)
    ACCESS_TOKEN_TTL: int = 60 * 24 * 7  # 7 days

    ENVIRONMENT: str

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
    INIT_CACHE: Dict[str, Any] = {}

    class Config:
        env_file = None


settings = Settings()  # type: ignore

cache = ThreadsafeCache(settings.INIT_CACHE)


class ExternalConfig(UserDict[str, str]):
    def __init__(self, config: Dict[str, str]):
        super().__init__(config)
        if config:
            self.parse_config(config)

    def parse_config(self, config: Dict[str, str]):
        self.cd_environments = config["continuous_deployment"]["environments"]
        self.cd_branches_accepted = [env["branch"] for env in self.cd_environments]
        self.cd_pullrequest_tag = config["continuous_deployment"]["pullrequest"]["tag"]
        self.cd_versions_available = config["continuous_deployment"]["pipeline"][
            "versions_available"
        ]
        self.watcher_user = config["watcher"]["user"]
        self.watcher_pwd = config["watcher"]["pwd"]
        self.vault_secret = config["su"]["vault_secret"]
        self.vault_mount = config["su"]["vault_mount"]


external_config: ExternalConfig = ExternalConfig({})
