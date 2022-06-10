from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Literal
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, Extra, Field


class BitbucketResource(BaseModel, extra=Extra.allow):
    """Base type for most resource objects. It defines the common type element that identifies an object's type"""

    type: str


class User(BaseModel, extra=Extra.allow):
    is_staff: bool
    account_id: str


class Link(BaseModel):
    name: str
    href: AnyHttpUrl


class Account(BitbucketResource, extra=Extra.allow):
    """An account object"""

    links: Dict[str, Link]
    username: str = Field(regex=r"^[a-zA-Z0-9_\-]+$")
    nickname: str
    account_status = "active"
    display_name: str
    website: str
    created_on: datetime
    uuid: UUID
    has_2fa_enabled: bool


class Author(BitbucketResource, extra=Extra.allow):
    raw: str
    user: Account


class Participant(BitbucketResource, extra=Extra.allow):
    user: Account | User
    role: Literal["PARTICIPANT", "REVIEWER"]
    approved: bool
    state: Literal["approved", "changes_requested", "null"]
    participated_on: datetime


class Project(BitbucketResource, extra=Extra.allow):
    links: Dict[str, Link]
    uuid: UUID
    key: str
    owner: Account
    name: str
    description: str
    is_private: bool
    created_on: datetime
    updated_on: datetime
    has_publicly_visible_repos: bool


class BaseCommit(BitbucketResource, extra=Extra.allow):
    hash: str = Field(regex=r"^[0-9a-f]{7,}?$")
    date: datetime
    author: Author
    message: str
    summary: BitbucketResource
    parents: List[BaseCommit] = []


class Commit(BitbucketResource, extra=Extra.allow):
    repository: Repository
    participants: List[Participant] = []


class Ref(BitbucketResource, extra=Extra.allow):
    links: Dict[str, Link] = {}
    name: str
    target: BaseCommit | Commit


class MergeStrategy(str, Enum):
    merge_commit = "merge_commit"
    squash = "squash"
    fast_forward = "fast_forward"


class Branch(BitbucketResource, extra=Extra.allow):
    merge_strategies: List[MergeStrategy] = []
    default_merge_strategy: MergeStrategy


class Repository(BitbucketResource, extra=Extra.allow):
    """A Bitbucket repository"""

    links: Dict[str, Link]
    uuid: UUID
    full_name: str
    is_private: bool
    parent: Repository | None = None
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


class PaginatedRepositories(BaseModel):
    """A paginated list of repositories"""

    size: int = Field(ge=0)
    page: int = Field(ge=1)
    pagelen: int = Field(ge=1)
    next: AnyHttpUrl
    previous: AnyHttpUrl
    values: List[Repository]


class WebhookEventKey(str, Enum):
    issue_comment_created = "issue:comment_created"
    issue_comment_updated = "issue:comment_updated"
    issue_created = "issue:created"
    issue_updated = "issue:updated"
    pr_approved = "pullrequest:approved"
    pr_change_request_removed = "pullrequest:changes_request_removed"
    pr_changes_requested = "pullrequest:changes_request_created"
    pr_comment_created = "pullrequest:comment_created"
    pr_comment_deleted = "pullrequest:comment_deleted"
    pr_comment_updated = "pullrequest:comment_updated"
    pr_created = "pullrequest:created"
    pr_declined = "pullrequest:rejected"
    pr_merged = "pullrequest:fulfilled"
    pr_unapproved = "pullrequest:unapproved"
    pr_updated = "pullrequest:updated"
    project_updated = "project:updated"
    repo_build_created = "repo:commit_status_created"
    repo_build_updated = "repo:commit_status_updated"
    repo_commit_comment_created = "repo:commit_comment_created"
    repo_created = "repo:created"
    repo_deleted = "repo:deleted"
    repo_forked = "repo:fork"
    repo_imported = "repo:imported"
    repo_push = "repo:push"
    repo_transfer = "repo:transfer"
    repo_updated = "repo:updated"
