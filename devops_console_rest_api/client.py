from asyncio import AbstractEventLoop
import asyncio
import inspect
from typing import Any, Dict

# from devops_sccs.plugins.bitbucketcloud import BitbucketCloud


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

    def threadsafe_async_partial(f, loop):
        def async_partial(*args, **kwargs):
            async def g():
                return f(*args, plugin_id=plugin_id, session=admin_session, **kwargs)

            future = asyncio.run_coroutine_threadsafe(g(), loop)
            return future.result(60)

        return async_partial

    for name, member in inspect.getmembers(core_sccs):
        if name.startswith("_"):
            continue
        if inspect.ismethod(member) or inspect.isfunction(member):
            f = threadsafe_async_partial(
                member,
                loop=loop,
            )
            setattr(bitbucket_client, name, f)
        # copy over properties from the core sccs client
        else:
            setattr(bitbucket_client, name, member)

    # let's keep a reference to the event loop so that we can batch api calls later on
    setattr(bitbucket_client, "loop", loop)
