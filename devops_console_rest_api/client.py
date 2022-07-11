from asyncio import AbstractEventLoop
import asyncio
from copy import deepcopy
import functools
import inspect
import logging
import types
from typing import Any, Dict

from devops_sccs.provision import Provision
from devops_console_rest_api.config import config
from requests import session


class Client:
    pass


bitbucket_client = Client()

# TODO remove need for this; it's an ugly hack to avoid having to refactor the
#      whole plugin architecture in order to avoid circular imports
def setup_bb_client(config: Dict[str, Any], core_sccs, loop: AbstractEventLoop) -> None:
    """
    Recreate the Bitbucket client with curried methods run in the parent thread.
    """

    vault_bitbucket: Dict[str, Any] = config.get("vault_bitbucket", {})

    if len(vault_bitbucket) == 0:
        raise Exception("vault_bitbucket not found in config")

    plugin_id = "cbq"
    admin_session = {
        "user": vault_bitbucket["username"],
        "apikey": vault_bitbucket["app_passwords"]["bitbucket_management"],
        "team": "croixbleue",
        "author": vault_bitbucket["email"],
    }

    global bitbucket_client

    async def async_partial(f, *args, **kwargs):
        result = f(*args, **kwargs)
        # if inspect.iscoroutinefunction(f):
        #     result = await result
        # elif inspect.isasyncgenfunction(f):
        #     # collect results from async generator
        #     result = [item async for item in result]

        return result

    def threadsafe_async_partial(f, loop):
        def g(*args, **kwargs):
            coro = async_partial(
                f, *args, plugin_id=plugin_id, session=admin_session, **kwargs
            )
            future = asyncio.run_coroutine_threadsafe(coro, loop)
            return future.result(3600)

        return g

    for name, method in inspect.getmembers(core_sccs, inspect.ismethod):
        if name.startswith("_"):
            continue
        f = threadsafe_async_partial(
            method,
            loop=loop,
        )
        # f = types.FunctionType(
        #     threadsafe_async_partial.__code__,
        #     threadsafe_async_partial.__globals__,
        #     name=name,
        #     argdefs=threadsafe_async_partial.__defaults__,
        #     closure=threadsafe_async_partial.__closure__,
        # )
        # f = functools.update_wrapper(f, method)
        # f.__kwdefaults__ = threadsafe_async_partial.__kwdefaults__
        setattr(bitbucket_client, name, f)
