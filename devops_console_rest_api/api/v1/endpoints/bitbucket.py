from devops_console_rest_api.client import bitbucket_client as client
from devops_console_rest_api.models.bitbucket import Repository
from fastapi import APIRouter
from pydantic import UUID4

router = APIRouter()


@router.get("/")
async def read_repos():
    return await client.get_repositories(args=None)


@router.post("/", response_model=Repository)
async def create_repo(repo: Repository):
    pass


@router.put("/{uuid}", response_model=Repository)
async def update_repo(uuid: UUID4):
    pass


@router.get("/{uuid}", response_model=Repository)
async def read_repo(uuid: UUID4):
    pass


@router.delete("/{uuid}", status_code=204)
async def delete_repo(uuid: UUID4):
    pass


@router.get("/subscribe_to_webhooks")
async def subscribe_to_webhooks():
    pass
