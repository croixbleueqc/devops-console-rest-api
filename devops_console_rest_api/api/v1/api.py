from fastapi import APIRouter, Security

from devops_console_rest_api.api.v1.endpoints import bitbucket, k8s
from devops_console_rest_api.auth import azure_scheme


api_router = APIRouter()

api_router.include_router(
    bitbucket.router,
    prefix="/repos",
    tags=["bitbucket"],
    dependencies=[Security(azure_scheme)],
)
api_router.include_router(k8s.router, prefix="/k8s", tags=["kubernetes"])
