from pydantic import AnyHttpUrl, BaseSettings, Field


config = {}


class Environment(BaseSettings):
    API_V1_STR = "/api/v1"
    HOOKS_API_STR = "/bitbucketcloud/hooks/repo"
    SECRET_KEY: str = Field(default="super secret key", env="SECRET_KEY")
    BACKEND_CORS_ORIGINS: list[str | AnyHttpUrl] = ["http://localhost:5001"]
    AAD_OPENAPI_CLIENT_ID: str = Field(default="", env="AAD_OPENAPI_CLIENT_ID")
    AAD_APP_CLIENT_ID: str = Field(default="", env="AAD_APP_CLIENT_ID")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


environment = Environment()
