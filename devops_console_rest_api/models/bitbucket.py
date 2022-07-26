from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, Generic, List, Literal, Optional, Type, TypeVar, TypedDict

from pydantic.generics import GenericModel

from pydantic import UUID4, AnyHttpUrl, BaseModel, Extra, Field


class BitbucketResource(BaseModel, extra=Extra.allow):
    """Base type for most resource objects. It defines the common type element that identifies an object's type"""

    type: str = ""


class User(BaseModel):
    is_staff: bool
    account_id: str


class Link(BaseModel):
    name: str | None
    href: AnyHttpUrl


class Account(BitbucketResource):
    """An account object"""

    links: Dict[str, Link] = {}
    username: str = Field(regex=r"^[a-zA-Z0-9_\-]+$")

    nickname: str = ""
    account_status = "active"
    display_name: str = ""
    website: str = ""
    created_on: datetime
    uuid: UUID4
    has_2fa_enabled: bool


class Author(BitbucketResource):
    raw: str
    user: Account


class Participant(BitbucketResource):
    user: Account | User
    role: Literal["PARTICIPANT", "REVIEWER"]
    approved: bool
    state: Literal["approved", "changes_requested", "null"]
    participated_on: datetime


class Project(BitbucketResource):
    links: Dict[str, Link] = {}
    uuid: UUID4 | None
    key: str
    owner: Account | None
    name: str | None
    description: str = ""
    is_private: bool = True
    created_on: datetime | None
    updated_on: datetime | None
    has_publicly_visible_repos: bool = False


class BaseCommit(BitbucketResource):
    hash: str = Field(regex=r"^[0-9a-f]{7,}?$")
    date: datetime
    author: Author
    message: str = ""
    summary: BitbucketResource
    parents: "List[BaseCommit]" = []


class Commit(BitbucketResource):
    repository: "Repository"
    participants: List[Participant] = []


class Ref(BitbucketResource):
    links: Dict[str, Link] = {}
    name: str
    target: BaseCommit | Commit


class MergeStrategy(str, Enum):
    merge_commit = "merge_commit"
    squash = "squash"
    fast_forward = "fast_forward"


class Branch(BitbucketResource):
    merge_strategies: List[MergeStrategy] = []
    default_merge_strategy: MergeStrategy


class Repository(BitbucketResource):
    """A Bitbucket repository"""

    links: Dict[str, Link]
    uuid: UUID4
    full_name: str
    is_private: bool
    parent: "Optional[Repository]" = None
    scm = "git"
    owner: Account
    name: str
    created_on: datetime
    updated_on: datetime
    size: int
    language: str
    has_issues: bool
    has_wiki: bool
    fork_policy: Literal["allow_forks", "no_public_forks", "no_forks"]
    project: Project
    mainbranch: Ref | Branch


class ProjectValue(TypedDict):
    name: str
    key: str


class ConfigOrPrivilegeValue(TypedDict):
    short: str
    key: str


class RepositoryPost(BaseModel, extra=Extra.allow):
    """Payload for creating a repository"""

    name: str
    description: str = ""
    project: ProjectValue
    configuration: ConfigOrPrivilegeValue
    privileges: ConfigOrPrivilegeValue
    scm = "git"


R = TypeVar("R", bound=BitbucketResource)


class Paginated(GenericModel, Generic[R]):
    """A paginated object"""

    size: int
    page: int
    pagelen: int
    next: Optional[AnyHttpUrl]
    previous: Optional[AnyHttpUrl]
    values: List[R]


class RepositoryPut(RepositoryPost):
    """Payload for updating a repository"""

    pass


class PaginatedRepositories(BaseModel):
    """A paginated list of repositories"""

    size: int = Field(ge=0)
    page: int = Field(ge=1)
    pagelen: int = Field(ge=1)
    next: AnyHttpUrl
    previous: AnyHttpUrl
    values: List[Repository]


BaseCommit.update_forward_refs()
Commit.update_forward_refs()
Repository.update_forward_refs()
