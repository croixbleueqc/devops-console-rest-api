import asyncio
import logging

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
            repository=repo.dict(),
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


@router.get("/create_default_webhooks")
async def create_default_webhooks():
    """Subscribe to webhooks for each repository (must be idempotent)."""

    # get list of repositories
    try:
        repos = await client.get_repositories(args=None)
    except Exception as e:
        logging.warn(f"Failed to get list of repositories: {e}")
        return

    subscriptions = []

    # we'll batch the requests since there are a lot of them, but note that the
    # rate limit for webhooks is 1000 reqs/hour, so just keep that in mind if
    # testing this out (there are roughly 400 repos at the time of writing)
    coros = []

    for repo in repos:

        async def _subscribe_if_not_set():
            try:
                current_subscriptions = await client.get_webhook_subscriptions(
                    repo_name=repo.name
                )
            except Exception as e:
                logging.warn(
                    f"Failed to get webhook subscriptions for {repo.name}: {e}"
                )
                return

            logging.warn(
                f"current_subscriptions for {repo.name}: {current_subscriptions}"
            )

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

            try:
                new_subscription = await client.create_webhook_subscription(
                    repo_name=repo.name,
                    url=WEBHOOKS_URL,
                    active=True,
                    events=WEBHOOKS_DEFAULT_EVENTS,
                    description=WEBHOOKS_DEFAULT_DESCRIPTION,
                )
            except Exception as e:
                logging.warn(
                    f"Failed to create webhook subscription for {repo.name}: {e}"
                )
                return

            logging.warn(f"Subscribed to default webhook for {repo.name}.")

            subscriptions.append(WebhookSubscription(**new_subscription))

        coros.append(_subscribe_if_not_set())

    await asyncio.gather(*coros)

    return subscriptions


@router.get("/remove_default_webhooks")
async def remove_default_webhooks():
    """Remove the default webhooks from all repositories."""

    # get list of repositories
    repos = await client.get_repositories(args=None)

    coros = []

    for repo in repos:

        async def _remove_default_webhooks():
            try:
                current_subscriptions = await client.get_webhook_subscriptions(
                    repo_name=repo.name
                )
            except Exception as e:
                logging.warn(
                    f"Failed to get webhook subscriptions for {repo.name}: {e}"
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
                        await client.delete_webhook_subscription(
                            repo_name=repo.name,
                            subscription_id=subscription["uuid"],
                        )
                        logging.warn(f"Deleted webhook subscription for {repo.name}.")
                    except Exception as e:
                        logging.warn(
                            f"Failed to delete webhook subscription for {repo.name}: {e}"
                        )
                        continue

            logging.info(f"Removed default webhooks from {repo.name}.")

        coros.append(_remove_default_webhooks())

    await asyncio.gather(*coros)


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
