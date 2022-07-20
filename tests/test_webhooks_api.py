import json
from http import HTTPStatus

import pytest
from devops_console_rest_api.client import bitbucket_client
from devops_console_rest_api.models.webhooks import WebhookEventKey
from devops_console_rest_api.webhooks_api.api import app
from fastapi.testclient import TestClient
from devops_sccs.atscached import atscached

from . import fixtures


@pytest.fixture
def mock_bitbucket_client(monkeypatch):
    @atscached()
    async def mock_get_repository(event):
        return "success"

    monkeypatch.setattr(bitbucket_client, "get_repository", mock_get_repository)
    setattr(bitbucket_client, "cd_branches_accepted", ["test"])
    monkeypatch.setattr(bitbucket_client, "cd_branches_accepted", ["test"])


client = TestClient(app)


def test_handle_webhook_event_invalid_body():
    response = client.post(
        "/",
        headers={"X-Event-Key": WebhookEventKey.repo_push.value},
        data="[]",
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_handle_webhook_event_invalid_header():
    response = client.post("/", headers={"X-Event-Key": "gibberish"}, data="{}")
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_handle_webhook_event_repo_push(mock_bitbucket_client):

    response = client.post(
        "/",
        headers={"X-Event-Key": WebhookEventKey.repo_push.value},
        data=json.dumps(fixtures.mock_repopushevent),
    )

    assert response.status_code == HTTPStatus.OK


def test_handle_webhook_event_repo_build_created(mock_bitbucket_client):
    # TODO: implement
    pass


def test_handle_webhook_event_repo_build_updated(mock_bitbucket_client):
    # TODO: implement
    pass


def test_handle_webhook_event_pr_created(mock_bitbucket_client):
    # TODO: implement
    pass


def test_handle_webhook_event_pr_updated(mock_bitbucket_client):
    # TODO: implement
    pass


def test_handle_webhook_event_pr_approved(mock_bitbucket_client):
    # TODO: implement
    pass


def test_handle_webhook_event_pr_declined(mock_bitbucket_client):
    # TODO: implement
    pass


def test_handle_webhook_event_pr_merged(mock_bitbucket_client):
    # TODO: implement
    pass
