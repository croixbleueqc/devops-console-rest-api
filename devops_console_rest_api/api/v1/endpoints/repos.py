from fastapi import APIRouter, HTTPException, Depends
from pydantic import UUID4

from devops_console_rest_api.models import Repo, RepoList, UserInDB
from devops_console_rest_api.api import deps
from devops_console_rest_api.clients import bb_client

client = bb_client


router = APIRouter()


@router.get("/", tags=["bitbucket"], response_model=RepoList)
async def read_repos():
    return RepoList(size=1, values=[Repo(name="test")])
    # repos = client.get_repos()
    # if not repos:
    #     raise HTTPException(status_code=404, detail="RepoList not found")
    # return repos


@router.post("/", tags=["bitbucket"], response_model=Repo)
async def create_repo(
    repo: Repo, current_user: UserInDB = Depends(deps.get_current_user)
):
    created = client.create_repo(repo)
    if not created:
        raise HTTPException(
            status_code=500, detail="Couldn't create repo, internal server error"
        )
    return created


@router.put("/{uuid}", tags=["bitbucket"], response_model=Repo)
async def update_repo(
    uuid: UUID4, current_user: UserInDB = Depends(deps.get_current_user)
):
    updated = client.update_repo(Repo(uuid=uuid))
    if not updated:
        raise HTTPException(status_code=400, detail="Bad request")
    return updated


@router.get("/{uuid}", tags=["bitbucket"], response_model=Repo)
async def read_repo(
    uuid: UUID4, current_user: UserInDB = Depends(deps.get_current_user)
):
    repo = client.get_repo_by_uuid(uuid)
    if not repo:
        raise HTTPException(
            status_code=404, detail=f'Couldn\'t find repo with uuid "{uuid}"'
        )
    return repo


@router.delete("/{uuid}", status_code=204)
async def delete_repo(
    uuid: UUID4, current_user: UserInDB = Depends(deps.get_current_user)
):
    res = client.delete_repo_by_uuid(uuid)
    if not res:
        raise HTTPException(status_code=404)
