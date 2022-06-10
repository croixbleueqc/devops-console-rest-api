import asyncio
import logging
import os
import threading

import uvicorn
import uvloop
from fastapi import FastAPI

from .api.v1.api import api_router
from .client import setup_bb_client
from .config import API_V1_STR, HOOKS_API_STR, config
from .webhooks_api.api import app as hooks_api


def init() -> FastAPI:
    """Initialize the FastAPI server."""

    app = FastAPI()

    app.include_router(api_router, prefix=API_V1_STR)

    return app


def mount_hooks_api(app: FastAPI):
    # The hook api runs in its own "subapp"; this means it has a separate api with
    # its own path operations. This reflects the concern that a change to Event-Horizon's
    # main API prefix (the version) should not affect the webhook endpoint, otherwise
    # we would need to update the urls for all existing subscriptions.
    app.mount(HOOKS_API_STR, hooks_api)
    logging.debug("Mounted hooks api")


def serve_threaded(cfg, core_sccs) -> threading.Thread:
    """Run server in it's own thread.
    Returns the thread object."""

    global config
    config = cfg

    setup_bb_client(config=cfg, core_sccs=core_sccs)

    app = init()

    # check if we need to start the hooks server
    if cfg["sccs"]["hook_server"] is not None:
        # TODO use values from hook_cfg
        mount_hooks_api(app)

    def serve(loop: asyncio.AbstractEventLoop):
        asyncio.set_event_loop(loop)
        try:
            uvicorn.run(
                app=app,
                host=cfg["sccs"]["hook_server"]["host"],
                port=cfg["sccs"]["hook_server"]["port"],
                log_level=int(os.environ.get("LOGGING_LEVEL", logging.DEBUG)),
            )
        except RuntimeError:
            logging.debug("FastAPI Server has stopped")

    # free performance boost (uvloop is already a dependency of fastapi)
    # https://github.com/MagicStack/uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    thread = threading.Thread(target=serve, args=(asyncio.new_event_loop(),))

    # ensure this thread dies with the main thread
    thread.daemon = True

    thread.start()

    return thread
