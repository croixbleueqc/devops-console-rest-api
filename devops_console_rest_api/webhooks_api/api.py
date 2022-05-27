import logging
from http import HTTPStatus
from devops_console_rest_api.clients.bitbucket import BitbucketRESTClient

from fastapi import FastAPI, HTTPException, Request

from ..core.config import cache
from ..core.config import external_config as config
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

client = BitbucketRESTClient()


@app.post("/", tags=["webhooks"])
async def handle_webhook_event(request: Request):
    """Handle a webhook event."""

    event_key = request.headers["X-Event-Key"]
    logging.info(f'Called handle_webhook_event with event key "{event_key}"')

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
            logging.warning(msg)
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=msg,
            )


async def handle_repo_push(event: RepoPushEvent):
    """Compare hook data to cached values and update cache accordingly."""
    logging.info('Handling "repo:push" webhook event')

    repository = event.repository
    changes = event.push["changes"]

    changesMatter = False
    for change in changes:
        branchName = change.new.name
        if branchName in config.cd_branches_accepted:
            changesMatter = True
            break

    if not changesMatter:
        logging.debug(
            f"branch not in environment accepted : {config.cd_versions_available}"
        )
        return

    config.hookWatcher.open_basic_session(config.watcherUser, config.watcherPwd)
    newVersionDeployed = await self._fetch_bitbucket_continuous_deployment_config(
        repoName, config.hookWatcher
    )
    await config.hookWatcher.close_session()

    logging.info(f"handle push detected new version : {newVersionDeployed}")
    cache["continuousDeploymentConfig"][repository.name] = newVersionDeployed


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