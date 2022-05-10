from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient

from devops_console_rest_api.main import app
from devops_console_rest_api.tests.utils.utils import get_superuser_token_headers


@pytest.fixture
def client() -> Generator:
    with TestClient(app) as c:
        yield c
    
@pytest.fixture
def superuser_token_headers(client: TestClient) -> Dict[str, str]:
    return get_superuser_token_headers(client)