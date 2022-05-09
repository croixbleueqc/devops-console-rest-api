from uuid import uuid4, UUID

from app.models import Repo, RepoList

MOCK_REPO_1 = Repo(uuid=UUID("915b0a11-cdb5-4ea0-8384-bd5c8c6a21b8"), name="cool_repo")
MOCK_REPO_2 = Repo(
    uuid=UUID("f7067107-05d2-4f34-8057-739a19b1e0b6"), name="awesome_repo"
)
MOCK_REPOS = RepoList(
    size=2,
    values=[MOCK_REPO_1, MOCK_REPO_2],
)


class BitBucketServerStub:
    def __init__(self):
        self._repos = MOCK_REPOS

    def get_repo(self, repo: Repo):
        return self._get_repo(repo)

    def get_repos(self):
        return self._repos

    def create_repo(self, repo: Repo):
        if not repo.uuid:
            repo.uuid = uuid4()

        # update dynamic store
        self._add_repo(repo)

        return repo

    def update_repo(self, repo: Repo):
        r = self.get_repo(repo)
        if not r:
            return None
        r = Repo(**repo.dict())

        # update dynamic store
        return self._update_repo(r)

    def delete_repo(self, repo: Repo):
        r = self._get_repo(repo)
        if not r:
            return None
        self._delete_repo(r)
        return True

    def _get_repo(self, repo: Repo):
        if repo.uuid:
            for r in self._repos.values:
                if r.uuid == repo.uuid:
                    return r
        elif repo.name:
            for r in self._repos.values:
                if r.name == repo.name:
                    return r
        return None

    def _add_repo(self, repo: Repo):
        self._repos.values.append(repo)
        self._update_len()

    def _update_repo(self, repo: Repo):
        for r in self._repos.values:
            if r.uuid == repo.uuid:
                r = repo
                return r
        return None

    def _delete_repo(self, repo: Repo):
        self._repos.values.remove(repo)
        self._update_len()

    def _update_len(self):
        self._repos.size = len(self._repos.values)
