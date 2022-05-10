"""
This type stub file was generated by pyright.
"""

from enum import Enum
from pydantic import BaseModel

"""
Typing for Pull Requests

https"""
class State(Enum):
    MERGED = ...
    SUPERSEDED = ...
    OPEN = ...
    DECLINED = ...
    def __str__(self) -> str:
        ...
    


class Branch(BaseModel):
    name = ...


class SrcDst(BaseModel):
    branch = ...


class LinksHref(BaseModel):
    href = ...


class Links(BaseModel):
    html = ...


class PullRequest(BaseModel):
    title = ...
    id = ...
    close_source_branch = ...
    source = ...
    destination = ...
    state = ...
    links = ...


