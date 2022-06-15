from functools import partial
import os
from typing import Any, Dict


class Client:
    def init(self, config: Dict[str, Any]) -> None:
        pass


bitbucket_client = Client()
k8s_client = Client()

# TODO remove need for this; it's an ugly hack to avoid having to refactor the
#      whole plugin architecture in order to avoid circular imports
def clone_client(original, clone, plugin_id, admin_session) -> None:
    # set curried methods
    for method in [m for m in dir(original) if callable(getattr(original, m))]:
        if method.startswith("_"):
            continue
        p = partial(
            getattr(original, method), plugin_id=plugin_id, session=admin_session
        )

        setattr(clone, str(method), p)

    # set properties
    for prop in [p for p in dir(original) if not callable(getattr(original, p))]:
        if prop.startswith("_"):
            continue
        setattr(clone, str(prop), getattr(original, prop))


def setup_clients(config: Dict[str, Any], core_sccs, core_k8s) -> None:
    vault_bitbucket: Dict[str, Any] | None = config.get("vault_bitbucket")

    if vault_bitbucket is None:
        raise Exception("vault_bitbucket not found in config")

    plugin_id = os.environ.get("PLUGIN_ID", "cbq")
    admin_session = {
        "user": vault_bitbucket["username"],
        "apikey": vault_bitbucket["app_passwords"]["bitbucket_management"],
        "team": "croixbleue",
        "author": vault_bitbucket["email"],
    }

    global bitbucket_client
    clone_client(
        original=core_sccs,
        clone=bitbucket_client,
        plugin_id=plugin_id,
        admin_session=admin_session,
    )

    global k8s_client
    clone_client(
        original=core_k8s,
        clone=k8s_client,
        plugin_id=plugin_id,
        admin_session=admin_session,
    )
