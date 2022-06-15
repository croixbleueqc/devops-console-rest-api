import asyncio
import logging
import os
import threading

import uvicorn
import uvloop
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1.api import api_router
from .auth import azure_scheme
from .client import setup_bb_client
from .config import environment, config
from .webhooks_api.api import app as hooks_api

app = FastAPI(
    swagger_ui_oauth2_redirect_url=f"{environment.API_V1_STR}/oauth2-redirect",  # should ba as configured in Azure AD
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": environment.AAD_OPENAPI_CLIENT_ID,
    },
)

if environment.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in environment.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event("startup")
async def load_openid_config() -> None:
    await azure_scheme.openid_config.load_config()


def init_app(config, core_sccs):
    """Initialize the FastAPI server with proper config."""
    global app

    setup_bb_client(config=config, core_sccs=core_sccs)

    app.include_router(api_router, prefix=environment.API_V1_STR)

    # check if we need to start the hooks server
    if config["sccs"]["hook_server"] is not None:
        # TODO use values from hook_cfg
        mount_hooks_api(app)

    logging.debug("FastAPI Server initialized")


def mount_hooks_api(app: FastAPI):
    # The hook api runs in its own "subapp"; this means it has a separate api with
    # its own path operations. This reflects the concern that a change to Event-Horizon's
    # main API prefix (the version) should not affect the webhook endpoint, otherwise
    # we would need to update the urls for all existing subscriptions.

    app.mount(environment.HOOKS_API_STR, hooks_api)
    logging.debug("Mounted hooks api")


def serve_threaded(cfg, core_sccs) -> threading.Thread:
    """Run server in it's own thread. Returns the thread object."""

    global app
    global config

    config = cfg

    init_app(config=config, core_sccs=core_sccs)

    def serve(loop: asyncio.AbstractEventLoop):
        asyncio.set_event_loop(loop)
        try:
            uvicorn.run(
                app="devops_console_rest_api.main:app",
                host=config["sccs"]["hook_server"]["host"],
                port=int(config["sccs"]["hook_server"]["port"]),
                log_level=str(os.environ.get("LOGGING_LEVEL", "debug")),
                reload=False,
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


if __name__ == "__main__":
    # Initialize the app with stub config and core sccs
    logging.warn("Starting server in main thread")
    init_app(config=config, core_sccs=None)
