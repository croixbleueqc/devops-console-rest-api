import asyncio
import logging, threading

import uvicorn
import uvloop
from devops_sccs.cache import Cache
from fastapi import FastAPI

from devops_console_rest_api.api.v1.api import api_router
from devops_console_rest_api.core import config
from devops_console_rest_api.webhooks_api.api import app as hooks_api


def init() -> FastAPI:
    app = FastAPI()

    app.include_router(api_router, prefix=config.settings.API_V1_STR)

    return app


def mount_hooks_api(app: FastAPI):
    # The hook api runs in its own "subapp"; this means it has a separate api with
    # its own path operations. This reflects the concern that a change to Event-Horizon's
    # main API prefix (the version) should not affect the webhook endpoint, otherwise
    # we would need to update the urls for all existing subscriptions.
    app.mount(config.settings.HOOKS_API_STR, hooks_api)
    logging.info("Mounted hooks api")


def run_threaded(cfg: dict, cache: Cache, hook_cfg: dict) -> threading.Thread:
    """Run server in it's own thread. Returns the thread object."""

    # override module cache with one supplied by caller
    config.cache = cache

    config.external_config = config.ExternalConfig(cfg)

    # initialize app
    app = init()

    # check if we need to start the hooks server
    if hook_cfg is not None:
        # TODO use values from hook_cfg
        mount_hooks_api(app)

    def serve(loop):
        asyncio.set_event_loop(loop)
        try:
            uvicorn.run(app)  # type: ignore
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
