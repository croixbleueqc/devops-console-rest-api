from asyncio import AbstractEventLoop
import logging
import os
import sys
from urllib.parse import urljoin

from .models.webhooks import WebhookEventKey


config = {}

ENVIRONMENT: str = "development"

API_V1_STR = "/api/v1"
WEBHOOKS_API_STR = "/bitbucketcloud/hooks/repo"

WEBHOOKS_HOST = os.environ.get("WEBHOOKS_HOST")
if WEBHOOKS_HOST is None:
    logging.error("WEBHOOKS_HOST environment variable not set")
    sys.exit(1)

WEBHOOKS_URL = urljoin(
    WEBHOOKS_HOST,
    WEBHOOKS_API_STR,
)

WEBHOOKS_DEFAULT_EVENTS = [
    WebhookEventKey.repo_push,
    WebhookEventKey.repo_build_created,
    WebhookEventKey.repo_build_updated,
    WebhookEventKey.pr_created,
    WebhookEventKey.pr_updated,
    WebhookEventKey.pr_approved,
    WebhookEventKey.pr_declined,
    WebhookEventKey.pr_merged,
]

WEBHOOKS_DEFAULT_DESCRIPTION = "Default webhook created via DevOps Console"
