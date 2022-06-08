from functools import partial
import os


class Client:
    pass


bitbucket_client = Client()

plugin_id = "cbq"
session = {
    "user": os.environ.get("BITBUCKET_USER"),
    "apikey": os.environ.get("BITBUCKET_APIKEY"),
    "team": "croixbleue",
    "author": os.environ.get("BITBUCKET_AUTHOR"),
}

# TODO remove need for this; it's an ugly hack to avoid having to refactor the
#      whole plugin architecture in order to avoid circular imports
def setup_bb_client(core_sccs) -> None:
    global bitbucket_client

    for method in [m for m in dir(core_sccs) if callable(getattr(core_sccs, m))]:
        if method.startswith("_") or method == "init" or method == "context":
            continue
        p = partial(getattr(core_sccs, method), plugin_id=plugin_id, session=session)

        setattr(bitbucket_client, str(method), p)

    setattr(bitbucket_client, "context", getattr(core_sccs, "context"))
