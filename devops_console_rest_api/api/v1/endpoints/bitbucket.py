import asyncio
import logging
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import UUID4

from devops_console_rest_api.client import bitbucket_client as bitbucket_client
from devops_console_rest_api.config import (
    WEBHOOKS_DEFAULT_DESCRIPTION,
    WEBHOOKS_DEFAULT_EVENTS,
    WEBHOOKS_URL,
)

from devops_console_rest_api.models.bitbucket import (
    Project,
    Repository,
    RepositoryPost,
)
from devops_console_rest_api.models.webhooks import WebhookSubscription
from aiobitbucket.errors import NetworkError

router = APIRouter()


@router.get("/repos")
async def read_repos():
    try:
        return await bitbucket_client.get_repositories()
    except NetworkError as e:
        logging.error(f"Error while getting repositories: {e.details}")
        raise HTTPException(status_code=e.status, detail=e.details)


@router.post("/repos")
async def create_repo(repo: RepositoryPost):
    """
    Create a new repository (if it doesn't exist) and set the webhooks.
    """

    try:
        responserepo = asyncio.run_coroutine_threadsafe(
            bitbucket_client.add_repository(
                repository=repo.dict(),
                template="empty-repo-for-applications",
                template_params={},
                args=None,
            ),
            loop=bitbucket_client.loop,
        ).result(10)
    except NetworkError as e:
        logging.error(f"Failed to create repository: {e.details}")
        raise HTTPException(status_code=e.status, detail=e.details)

    if not responserepo:
        raise HTTPException(status_code=400, detail="Failed to create repository")

    # Set the default webhook
    try:
        asyncio.run_coroutine_threadsafe(
            bitbucket_client.create_webhook_subscription(
                repo_name=repo.name,
                url=WEBHOOKS_URL,
                active=True,
                events=WEBHOOKS_DEFAULT_EVENTS,
                description=WEBHOOKS_DEFAULT_DESCRIPTION,
                args=None,
            ),
            bitbucket_client.loop,
        )
    except NetworkError as e:
        logging.error(e)
        raise HTTPException(status_code=e.status, detail=e.details)

    return responserepo


@router.get("/repos/create_default_webhooks")
async def create_default_webhooks():
    """Subscribe to webhooks for each repository (must be idempotent)."""

    # get list of repositories
    try:
        repos = await bitbucket_client.get_repositories()
    except NetworkError as e:
        logging.warn(f"Failed to get list of repositories: {e}")
        raise HTTPException(status_code=e.status, detail=e.details)

    subscriptions = []

    # we'll batch the requests since there are a lot of them, but note that the
    # rate limit for webhooks is 1000 reqs/hour, so just keep that in mind if
    # testing this out (there are roughly 400 repos at the time of writing)
    coros = []

    for repo in repos:

        async def _subscribe_if_not_set(repo):
            # get list of webhooks for this repo
            try:
                current_subscriptions = (
                    await bitbucket_client.get_webhook_subscriptions(
                        repo_name=repo.name
                    )
                )
            except NetworkError as e:
                logging.warn(
                    f"Failed to get webhook subscriptions for {repo.name}: {e.details}"
                )
                return

            # check if the webhook is already set
            if any(
                [
                    subscription["url"] == WEBHOOKS_URL
                    and all(
                        [
                            event in subscription["events"]
                            for event in WEBHOOKS_DEFAULT_EVENTS
                        ]
                    )
                    for subscription in current_subscriptions["values"]
                ]
            ):
                logging.warn(f"Webhook subscription already exists for {repo.name}.")
                return

            # create the webhook
            try:
                new_subscription = await bitbucket_client.create_webhook_subscription(
                    repo_name=repo.name,
                    url=WEBHOOKS_URL,
                    active=True,
                    events=WEBHOOKS_DEFAULT_EVENTS,
                    description=WEBHOOKS_DEFAULT_DESCRIPTION,
                )
                logging.warn(f"Subscribed to default webhook for {repo.name}.")
            except NetworkError as e:
                logging.warn(
                    f"Failed to create webhook subscription for {repo.name}: {e.details}"
                )
                return

            subscriptions.append(WebhookSubscription(**new_subscription))

        coros.append(_subscribe_if_not_set(repo))

    await asyncio.gather(*coros)

    return subscriptions


@router.get("/repos/remove_default_webhooks")
async def remove_default_webhooks():
    """Remove the default webhooks from all repositories."""

    # get list of repositories
    try:
        repos = await bitbucket_client.get_repositories()
    except NetworkError as e:
        logging.warn(f"Failed to get list of repositories: {e.details}")
        return

    coros = []

    for repo in repos:

        async def _remove_default_webhooks(repo):
            try:
                current_subscriptions = (
                    await bitbucket_client.get_webhook_subscriptions(
                        repo_name=repo.name
                    )
                )
            except NetworkError as e:
                logging.warn(
                    f"Failed to get webhook subscriptions for {repo.name}: {e.details}"
                )
                return

            if (
                current_subscriptions is None
                or len(current_subscriptions["values"]) == 0
            ):
                logging.warn(f"No webhook subscriptions for {repo.name}.")
                return

            for subscription in current_subscriptions["values"]:
                if subscription["url"] == WEBHOOKS_URL:
                    try:
                        await bitbucket_client.delete_webhook_subscription(
                            repo_name=repo.name,
                            subscription_id=subscription["uuid"],
                        )
                        logging.warn(f"Deleted webhook subscription for {repo.name}.")
                    except NetworkError as e:
                        logging.warn(
                            f"Failed to delete webhook subscription for {repo.name}: {e.details}"
                        )
                        continue

            logging.info(f"Removed default webhooks from {repo.name}.")

        coros.append(_remove_default_webhooks(repo))

    await asyncio.gather(*coros)


@router.put("/repos/{uuid}", response_model=Repository)
async def update_repo(uuid: UUID4):
    pass


@router.delete("/{repo_name}", status_code=204)
async def delete_repo(repo_name: str):
    try:
        await bitbucket_client.delete_repository(repo_name=repo_name)
    except NetworkError as e:
        logging.error(f"Failed to delete repository: {e.details}")
        raise HTTPException(status_code=e.status, detail=e.details)


@router.get("/repos/by-uuid/{uuid}", response_model=Repository)
async def get_repo_by_uuid(uuid: UUID4):
    return await bitbucket_client.get_repository(args={"uuid": uuid})


@router.get("/repos/by-name/{name}", response_model=Repository)
async def get_repo_by_name(name: str):
    return await bitbucket_client.get_repository(repository=name)


# ------------------------------------------------------------------------------
# Projects
# ------------------------------------------------------------------------------


@router.get("/projects", response_model=List[Project])
async def get_projects():
    try:
        return await bitbucket_client.get_projects()
    except NetworkError as e:
        logging.error(f"Failed to get list of projects: {e.details}")
        raise HTTPException(status_code=e.status, detail=e.details)
