import logging
import os
import sys
from urllib.parse import urljoin

from .models.bitbucket import WebhookEventKey


config = {}

ENVIRONMENT: str = "development"

API_V1_STR = "/api/v1"
HOOKS_API_STR = "/bitbucketcloud/hooks/repo"

WEBHOOKS_HOST = os.environ.get("WEBHOOKS_HOST")
if WEBHOOKS_HOST is None:
    logging.error("WEBHOOKS_HOST environment variable not set")
    sys.exit(1)

WEBHOOKS_URL = urljoin(
    WEBHOOKS_HOST,
    HOOKS_API_STR,
)

WEBHOOKS_DEFAULT_EVENTS = [
    WebhookEventKey.repo_push,
    WebhookEventKey.repo_build_created,
    WebhookEventKey.repo_build_updated,
]

WEBHOOKS_DEFAULT_DESCRIPTION = "Default webhook created via DevOps Console"
