import secrets
from typing import Any, Dict, List

from devops_sccs.cache import ThreadsafeCache
from pydantic import BaseModel, BaseSettings, EmailStr


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
    INIT_CACHE: Dict[str, Any] = {}

    class Config:
        env_file = None


environment = Environment()

cache = ThreadsafeCache(environment.INIT_CACHE)


class ExternalConfig(BaseModel):
    cd_environments: List[Dict[str, Any]]
    cd_branches_accepted: List[str]
    cd_pullrequest_tag: str
    cd_versions_available: List[str]

    # TODO should probably be renamed to "bitbucket_username"
    watcher_user: str
    # bitbucket_password
    watcher_pwd: str

    vault_secret: str
    vault_mount: str

    team: str


def flatten_external_config(config: Dict[str, Any]):

    cd_environments = config["continuous_deployment"]["environments"]
    cd_branches_accepted = [env["branch"] for env in cd_environments]

    return ExternalConfig(
        cd_environments=cd_environments,
        cd_branches_accepted=cd_branches_accepted,
        cd_pullrequest_tag=config["continuous_deployment"]["pullrequest"]["tag"],
        cd_versions_available=config["continuous_deployment"]["pipeline"][
            "versions_available"
        ],
        watcher_user=config["watcher"]["user"],
        watcher_pwd=config["watcher"]["pwd"],
        vault_secret=config["su"]["vault_secret"],
        vault_mount=config["su"]["vault_mount"],
        team=config["team"],
    )


external_config: ExternalConfig | None = None
