from fastapi import FastAPI
from fastapi.testclient import TestClient

from devops_console_rest_api.api.v1.endpoints.bitbucket import router

app = FastAPI()

app.include_router(router)

client = TestClient(app)
