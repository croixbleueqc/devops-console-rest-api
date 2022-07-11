import logging
from typing import Any

from fastapi import APIRouter
from pydantic import UUID4

from devops_console_rest_api.client import bitbucket_client as client
from devops_console_rest_api.config import (
    WEBHOOKS_DEFAULT_DESCRIPTION,
    WEBHOOKS_DEFAULT_EVENTS,
    WEBHOOKS_URL,
)
from devops_console_rest_api.models.bitbucket import (
    Repository,
    RepositoryPost,
    PaginatedRepositories,
)
from devops_console_rest_api.models.webhooks import WebhookSubscription

router = APIRouter()


@router.get("/")
async def read_repos():
    return await client.get_repositories(args=None)


@router.post("/")
async def create_repo(repo: RepositoryPost):
    """
    Create a new repository (if it doesn't exist) and set the webhooks.
    """

    try:
        responserepo = await client.add_repository(
            repository=repo,
            template="empty-repo-for-applications",
            template_params=repo.dict(),
            args=None,
        )
    except Exception as e:
        logging.error(e)
        raise e

    if not responserepo:
        raise Exception("Failed to create repository")

    # Set the default webhook
    try:
        await client.create_webhook_subscription(
            repo_name=repo.name,
            url=WEBHOOKS_URL,
            active=True,
            events=WEBHOOKS_DEFAULT_EVENTS,
            description=WEBHOOKS_DEFAULT_DESCRIPTION,
            args=None,
        )
    except Exception as e:
        logging.error(e)
        raise e

    return responserepo


@router.get("/subscribe_all_webhooks")
async def subscribe_all_webhooks():
    """Subscribe to webhooks for each repository (must be idempotent)."""

    # get list of repositories
    repos = await client.get_repositories(args=None)

    subscriptions = []
    for repo in repos:
        current_subscriptions = await client.get_webhook_subscriptions(
            repo_name=repo.name
        )

        async def _subscribe_if_not_set():
            for subscription in current_subscriptions["values"]:
                if subscription["url"] == WEBHOOKS_URL and all(
                    [
                        event in subscription["events"]
                        for event in WEBHOOKS_DEFAULT_EVENTS
                    ]
                ):
                    logging.info(f"webhook subscription already exists for {repo.name}")
                    return

                new_subscription = await client.create_webhook_subscription(
                    repo_name=repo.name,
                    url=WEBHOOKS_URL,
                    active=True,
                    events=WEBHOOKS_DEFAULT_EVENTS,
                    description=WEBHOOKS_DEFAULT_DESCRIPTION,
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
