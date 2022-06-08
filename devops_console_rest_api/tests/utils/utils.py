from typing import Dict
from fastapi.testclient import TestClient

from devops_console_rest_api.core.environment import settings


def get_superuser_token_headers(client: TestClient) -> Dict[str, str]:
    credentials = {
        "username": settings.SUPERUSER_USERNAME,
        "password": settings.SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=credentials)
    tokens = r.json()
    access_token = tokens["access_token"]

    return {"Authorization": f"Bearer {access_token}"}
