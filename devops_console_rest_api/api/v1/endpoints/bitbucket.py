import logging
import os
from typing import List
from urllib.parse import urljoin
from devops_console_rest_api.client import bitbucket_client as client
from devops_console_rest_api.config import environment
from devops_console_rest_api.models.bitbucket import (
    Repository,
    WebhookEventKey,
)
from devops_console_rest_api.models.webhooks import WebhookSubscription
from fastapi import APIRouter
from pydantic import UUID4

router = APIRouter()


@router.get("/")
async def read_repos():
    return await client.get_repositories(args=None)


@router.post("/", response_model=Repository)
async def create_repo(repo: Repository):
    pass


@router.get("/subscribe_all_webhooks")
async def subscribe_all_webhooks():
    """Subscribe to webhooks for each repository (must be idempotent)."""

    trigger_events = [WebhookEventKey.repo_push, WebhookEventKey.repo_build_updated]

    # get list of repositories
    repos = await client.get_repositories(args=None)

    host = os.environ.get(
        "HOST", "https://event-horizon-backend-poc.svcnp.canassurance.com"
    )
    endpoint = environment.HOOKS_API_STR
    url = urljoin(host, endpoint)

    subscriptions = []
    for repo in repos:
        current_subscriptions = await client.get_webhook_subscriptions(
            repo_name=repo.name
        )

        async def _subscribe_if_not_set():
            for subscription in current_subscriptions["values"]:
                if subscription["url"] == url and all(
                    [event in subscription["events"] for event in trigger_events]
                ):
                    logging.info(f"webhook subscription already exists for {repo.name}")
                    return

                new_subscription = await client.create_webhook_subscription(
                    repo_name=repo.name,
                    url=url,
                    active=True,
                    events=trigger_events,
                    description="This webhook has been set via api.",
                )

                subscriptions.append(WebhookSubscription(**new_subscription))

        await _subscribe_if_not_set()

    return subscriptions


@router.put("/{uuid}", response_model=Repository)
async def update_repo(uuid: UUID4):
    pass


@router.get("/by-uuid/{uuid}", response_model=Repository)
async def get_repo_by_uuid(uuid: UUID4):
    return await client.get_repository(args={"uuid": uuid})


@router.get("/by-name/{name}", response_model=Repository)
async def get_repo_by_name(name: str):
    return await client.get_repository(repository=name, args=None)


@router.delete("/{uuid}", status_code=204)
async def delete_repo(uuid: UUID4):
    pass
