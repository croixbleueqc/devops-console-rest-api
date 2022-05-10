from pydantic import BaseModel, Field, UUID4


class Repo(BaseModel):
    uuid: UUID4 | None = None
    name: str | None = Field("default", regex="^[a-zA-Z0-9_-]+$")


class RepoList(BaseModel):
    size: int
    values: list[Repo]
