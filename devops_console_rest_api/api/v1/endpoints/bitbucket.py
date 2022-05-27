from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import UUID4

from ....clients.bitbucket import BitbucketRESTClient
from ....models.bitbucket import Repository

client = BitbucketRESTClient()

router = APIRouter()


@router.get("/", response_model=List[Repository])
async def read_repos() -> List[Repository]:
    repos = await client.get_repos()
    if not repos:
        raise HTTPException(status_code=404, detail="RepoList not found")
    return repos


@router.post("/", response_model=Repository)
async def create_repo(repo: Repository):
    created = await client.create_repo(repo)
    if not created:
        raise HTTPException(
            status_code=500, detail="Couldn't create repo, internal server error"
        )
    return created


@router.put("/{uuid}", response_model=Repository)
async def update_repo(uuid: UUID4):
    updated = await client.update_repo(Repo(uuid=uuid))
    if not updated:
        raise HTTPException(status_code=400, detail="Bad request")
    return updated


@router.get("/{uuid}", response_model=Repository)
async def read_repo(uuid: UUID4):
    repo = await client.get_repo_by_uuid(uuid)
    if not repo:
        raise HTTPException(
            status_code=404, detail=f'Couldn\'t find repo with uuid "{uuid}"'
        )
    return repo


@router.delete("/{uuid}", status_code=204)
async def delete_repo(uuid: UUID4):
    res = await client.delete_repo_by_uuid(uuid)
    if not res:
        raise HTTPException(status_code=404)
