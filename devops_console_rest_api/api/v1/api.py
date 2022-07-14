from devops_console_rest_api.api.v1.endpoints import bitbucket, k8s
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(bitbucket.router, prefix="/bb", tags=["bitbucket"])
api_router.include_router(k8s.router, prefix="/k8s", tags=["kubernetes"])
