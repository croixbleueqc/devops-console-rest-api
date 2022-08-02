import logging
import os

import uvicorn
from fastapi import FastAPI

from .api.v1.router import router
from .client import setup_bb_client
from .config import API_V1_STR, WEBHOOKS_API_STR, config
from .webhooks_server.app import app as webhooks_server

app = FastAPI()


def init_app(config, core_sccs, loop) -> None:
    """Initialize the FastAPI server."""
    global app

    setup_bb_client(config=config, core_sccs=core_sccs, loop=loop)

    app.include_router(router, prefix=API_V1_STR)

    # check if we need to start the hooks server
    if config["sccs"]["hook_server"] is not None:
        # TODO use values from hook_cfg
        mount_webhooks_server(app)

    logging.debug("FastAPI Server initialized")


def mount_webhooks_server(app: FastAPI):
    # The hook api runs in its own "subapp"; this means it has a separate api with
    # its own path operations. This reflects the concern that a change to Event-Horizon's
    # main API prefix (the version) should not affect the webhook endpoint, otherwise
    # we would need to update the urls for all existing subscriptions.

    app.mount(WEBHOOKS_API_STR, webhooks_server)
    logging.debug("Mounted webhooks server")


async def run(cfg, core_sccs, loop):
    """Run the FastAPI server."""

    global app
    global config

    config = cfg

    init_app(config=config, core_sccs=core_sccs, loop=loop)

    config = uvicorn.Config(
        app="devops_console_rest_api:main.app",
        host=config["sccs"]["hook_server"]["host"],
        port=int(config["sccs"]["hook_server"]["port"]),
        log_level=str(os.environ.get("LOGGING_LEVEL", "debug")),
        reload=False,
    )
    server = uvicorn.Server(config)

    try:
        await server.serve()
    except RuntimeError:
        logging.debug("FastAPI Server has stopped")
