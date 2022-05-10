from fastapi import FastAPI

from devops_console_rest_api.api.v1.api import api_router
from devops_console_rest_api.core.config import settings


app = FastAPI()


app.include_router(api_router, prefix=settings.API_V1_STR)
