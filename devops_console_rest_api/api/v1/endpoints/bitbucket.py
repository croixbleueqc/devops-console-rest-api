import logging
import os
from typing import List
from urllib.parse import urljoin
from devops_console_rest_api.client import bitbucket_client as client
from devops_console_rest_api.config import HOOKS_API_STR
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


@router.get(
    "/subscribe_to_push_event_webhooks", response_model=List[WebhookSubscription]
)
async def subscribe_to_push_event_webhooks():
    """Subscribe to webhooks for each repository (must be idempotent)."""

    # get list of repositories
    repos = await client.get_repositories(args=None)
    host = os.environ.get("HOST", "http://localhost:5001")
    endpoint = HOOKS_API_STR
    url = urljoin(host, endpoint)

    subscriptions = []
    for repo in repos:
        # check if webhook already exists
        # create webhook subscription
        subscription = None
        try:
            subscription = await client.create_webhook_subscription(
                repo_name=repo._name,
                url=url,
                active=True,
                events=[WebhookEventKey.repo_push],
                description="",
            )
        except Exception as e:
            logging.error(f"Error creating webhook subscription for {repo._name}: {e}")
        finally:
            if subscription is not None:
                subscriptions.append(WebhookSubscription(**subscription))
            continue

    return subscriptions


@router.get("/subscribe_to_webhook_test", response_model=WebhookSubscription)
async def subscribe_to_webhook_test():
    host = os.environ.get("HOST", "http://localhost:5001")
    endpoint = HOOKS_API_STR
    url = urljoin(host, endpoint)
    repo_name = "aiobitbucket-wip"
    subscription = None
    try:
        subscription = await client.create_webhook_subscription(
            repo_name=repo_name,
            url=url,
            active=True,
            events=[WebhookEventKey.repo_push],
            description="set by bb admin...",
        )
    except Exception as e:
        logging.error(f"Error creating webhook subscription: {e}")

    logging.info(f"subscription created: {subscription}")

    if subscription is not None:
        return WebhookSubscription(**subscription)
    else:
        logging.warn(f"unable to create webhook subscription for {repo_name}")


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
