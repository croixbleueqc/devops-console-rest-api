import logging
from http import HTTPStatus
from devops_console_rest_api.client import bitbucket_client as client

from fastapi import FastAPI, HTTPException, Request

from ..models.bitbucket import WebhookEventKey
from ..models.webhooks import (
    PRApprovedEvent,
    PRCreatedEvent,
    PRDeclinedEvent,
    PRMergedEvent,
    PRUpdatedEvent,
    RepoBuildStatusCreated,
    RepoBuildStatusUpdated,
    RepoPushEvent,
)

app = FastAPI()


@app.post("/", tags=["bitbucket_webhooks"])
async def handle_webhook_event(request: Request):
    """Handle a webhook event."""

    event_key = request.headers["X-Event-Key"]
    logging.info(f'Receive webhook with event key "{event_key}"')

    body = await request.json()

    match event_key:
        case WebhookEventKey.repo_push:
            return await handle_repo_push(event=RepoPushEvent(**body))
        case WebhookEventKey.repo_build_created:
            return handle_commit_status_created(event=RepoBuildStatusCreated(**body))
        case WebhookEventKey.repo_build_updated:
            return handle_build_status_updated(event=RepoBuildStatusUpdated(**body))
        case WebhookEventKey.pr_created:
            return handle_pr_created(event=PRCreatedEvent(**body))
        case WebhookEventKey.pr_updated:
            return handle_pr_updated(event=PRUpdatedEvent(**body))
        case WebhookEventKey.pr_approved:
            return handle_pr_approved(event=PRApprovedEvent(**body))
        case WebhookEventKey.pr_declined:
            return handle_pr_declined(event=PRDeclinedEvent(**body))
        case WebhookEventKey.pr_merged:
            return handle_pr_merged(event=PRMergedEvent(**body))
        case _:
            msg = (f"Unsupported event key: {event_key}",)
            logging.warn(msg)
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=msg,
            )


async def handle_repo_push(event: RepoPushEvent):
    """Compare hook data to cached values and update cache accordingly."""

    logging.info('Handling "repo:push" webhook event')

    # determine if the push event touches any of the cached values
    changes_matter = False
    for push_change in event.push["changes"]:
        if (
            push_change.new.type == "branch"
            and push_change.new.name in client.cd_branches_accepted
        ):
            changes_matter = True
            break

    # if the push event doesn't touch any of the cached values, we can skip it
    if not changes_matter:
        logging.info("Push event doesn't touch any of the cached values")
        return

    # if it does, we need to update the cache
    logging.info("Push event touches cached values, updating cache")
    await client.get_repository.clear_cache()
    # TODO: update more than just this function


def handle_commit_status_created(event: RepoBuildStatusCreated):
    pass


def handle_build_status_updated(event: RepoBuildStatusUpdated):
    pass


def handle_pr_created(event: PRCreatedEvent):
    pass


def handle_pr_updated(event: PRUpdatedEvent):
    pass


def handle_pr_merged(event: PRMergedEvent):
    pass


def handle_pr_approved(event: PRApprovedEvent):
    pass


def handle_pr_declined(event: PRDeclinedEvent):
    pass
