from uuid import UUID

from devops_console_rest_api import models
from aiobitbucket.bitbucket import Bitbucket as Bitbucket_Client
from devops_console_rest_api.core.config import settings

client = Bitbucket_Client()

async def bb_query(fn):
    client.open_basic_session(settings.USERNAME, settings.PASSWORD)
    await fn()
    await client.close_session()



class BitBucketRESTClient:
    def get_repo_by_uuid(self, uuid: UUID):
        return server.get_repo(models.Repo(uuid=uuid))

    def get_repos(self):
        return server.get_repos()

    def create_repo(self, repo: models.Repo):
        return server.create_repo(repo)

    def update_repo(self, repo: models.Repo):
        return server.update_repo(repo)

    def delete_repo_by_uuid(self, uuid: UUID):
        return server.delete_repo(models.Repo(uuid=uuid))


bb_client = BitBucketRESTClient()
