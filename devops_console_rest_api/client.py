from functools import partial
from typing import Any, Dict


class Client:
    pass


bitbucket_client = Client()

# TODO remove need for this; it's an ugly hack to avoid having to refactor the
#      whole plugin architecture in order to avoid circular imports
def setup_bb_client(config: Dict[str, Any], core_sccs) -> None:
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

    # set verbatim methods
    # setattr(bitbucket_client, "__init__", getattr(core_sccs, "__init__"))
    # setattr(bitbucket_client, "init", getattr(core_sccs, "init"))

    # set curried methods
    for method in [m for m in dir(core_sccs) if callable(getattr(core_sccs, m))]:
        if method.startswith("_") or method == "init":
            continue
        p = partial(
            getattr(core_sccs, method), plugin_id=plugin_id, session=admin_session
        )

        setattr(bitbucket_client, str(method), p)

    # set properties
    for prop in [p for p in dir(core_sccs) if not callable(getattr(core_sccs, p))]:
        if prop.startswith("_"):
            continue
        setattr(bitbucket_client, str(prop), getattr(core_sccs, prop))
