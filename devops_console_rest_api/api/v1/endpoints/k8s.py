from fastapi import APIRouter, Query
from devops_console_rest_api.client import k8s_client as client

router = APIRouter()


@router.get("/", tags=["kubernetes"])
async def list_pods(repo: str = Query(default=None), env: str = Query(default=None)):
    return await client.list_pods(repository=repo, environment=env)
