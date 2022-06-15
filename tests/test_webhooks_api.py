from devops_console_rest_api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_can_get_webhooks_list():
    # TODO
    pass


def test_subscribe_to_webhook():
    # TODO
    pass
