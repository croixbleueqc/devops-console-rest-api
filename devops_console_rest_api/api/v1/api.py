from fastapi import APIRouter

from devops_console_rest_api.api.v1.endpoints import bitbucket, k8s, login


api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(bitbucket.router, prefix="/repos", tags=["bitbucket"])
api_router.include_router(k8s.router, prefix="/k8s", tags=["kubernetes"])
