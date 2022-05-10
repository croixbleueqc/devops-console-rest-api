from uuid import UUID

from app import models, server_stubs
from aiobitbucket import bitbucket as bitbucket_client

client = bitbucket_client()

def bb_query(fn):


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
