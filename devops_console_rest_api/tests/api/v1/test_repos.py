from typing import Dict
from uuid import uuid4
from fastapi.testclient import TestClient

from devops_console_rest_api.core.environment import settings


def test_read_repos(client: TestClient, superuser_token_headers: Dict[str, str]):
    res = client.get(f"{settings.API_V1_STR}/repos/", headers=superuser_token_headers)
    assert res.status_code == 200


def test_read_non_existing_repo(
    client: TestClient, superuser_token_headers: Dict[str, str]
):
    uuid = uuid4()
    res = client.get(
        f"{settings.API_V1_STR}/repos/{uuid}", headers=superuser_token_headers
    )
    assert res.status_code == 404
    assert res.json() == {"detail": f'Couldn\'t find repo with uuid "{uuid}"'}


def test_read_gireposerish_repo(
    client: TestClient, superuser_token_headers: Dict[str, str]
):
    res = client.get(
        f"{settings.API_V1_STR}/repos/aifuadskjg", headers=superuser_token_headers
    )
    assert res.status_code == 422


def test_read_existing_repo(
    client: TestClient, superuser_token_headers: Dict[str, str]
):
    res = client.get(
        f"{settings.API_V1_STR}/repos/915b0a11-cdb5-4ea0-8384-bd5c8c6a21b8",
        headers=superuser_token_headers,
    )
    assert res.status_code == 200
    assert res.json() == {
        "uuid": "915b0a11-cdb5-4ea0-8384-bd5c8c6a21b8",
        "name": "cool_repo",
    }


def test_create_invalid_repo(
    client: TestClient, superuser_token_headers: Dict[str, str]
):
    res = client.post(
        f"{settings.API_V1_STR}/repos/",
        json={"name": "invalid name %"},
        headers=superuser_token_headers,
    )
    assert res.status_code == 422


def test_create_valid_repo(client: TestClient, superuser_token_headers: Dict[str, str]):
    repos = client.get(f"{settings.API_V1_STR}/repos/", headers=superuser_token_headers)
    num = repos.json()["size"]

    res = client.post(
        f"{settings.API_V1_STR}/repos/",
        headers=superuser_token_headers,
        json={"name": "test_repo"},
    )
    assert res.status_code == 200

    # test that repo was properly created
    uuid = res.json()["uuid"]
    res = client.get(
        f"{settings.API_V1_STR}/repos/{uuid}", headers=superuser_token_headers
    )
    assert res.status_code == 200
    assert res.json()["name"] == "test_repo"

    # test that repolist reflects the change
    repos = client.get(f"{settings.API_V1_STR}/repos/", headers=superuser_token_headers)
    new_num = repos.json()["size"]
    assert new_num - num == 1


def test_delete_nonexistant_repo(
    client: TestClient, superuser_token_headers: Dict[str, str]
):
    res = client.delete(
        f"{settings.API_V1_STR}/repos/{uuid4()}", headers=superuser_token_headers
    )
    assert res.status_code == 404


def test_delete_exisiting_repo(
    client: TestClient, superuser_token_headers: Dict[str, str]
):
    res = client.delete(
        f"{settings.API_V1_STR}/repos/915b0a11-cdb5-4ea0-8384-bd5c8c6a21b8",
        headers=superuser_token_headers,
    )
    assert res.status_code == 204
