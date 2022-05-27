from contextlib import asynccontextmanager
from typing import Callable, List, ParamSpec, TypeVar
from uuid import UUID
from aiobitbucket.apis.repositories.repository import RepoSlug

from aiobitbucket.bitbucket import Bitbucket as Bitbucket_Client
from devops_console_rest_api.core.config import external_config as config
from devops_console_rest_api.models.bitbucket import Repository

client = Bitbucket_Client()

P = ParamSpec("P")
R = TypeVar("R")


@asynccontextmanager
async def bitbucket_session_context_manager():
    await client.open_basic_session(config.watcher_user, config.watcher_pwd)
    try:
        yield client
    finally:
        await client.close_session()


async def with_bitbucket_session(fn: Callable[P, R]) -> Callable[P, R]:
    async def diddle(*args: P.args, **kwargs: P.kwargs) -> R:
        async with bitbucket_session_context_manager() as cli:
            return await fn(cli, *args, **kwargs)

    return diddle


class BitbucketRESTClient:
    @with_bitbucket_session
    async def get_repo_by_uuid(self, uuid: UUID) -> Repository | None:
        return None

    @with_bitbucket_session
    async def get_repos(self) -> List[Repository]:
        return []

    @with_bitbucket_session
    async def create_repo(self, repo: Repository) -> Repository | None:
        return None

    @with_bitbucket_session
    def update_repo(self, repo: Repository) -> Repository | None:
        return None

    @with_bitbucket_session
    def delete_repo_by_uuid(self, uuid: UUID) -> None:
        pass

    @with_bitbucket_session
    async def fetch_contiuous_deployment_config(
        self, cli: Bitbucket_Client, repo_name: str
    ):
        """Fetch a list of deployed versions of a repository."""

        repo: RepoSlug = cli.repositories.repo_slug(config.team, repo_name)

        # Get supported branches
        async for branch in repo.refs().branches.get():
            try:
                index = config.cd_branches_accepted.index(branch.name)
                if (
                    environments is None
                    or self.cd_environments[index]["name"] in environments
                ):
                    deploys.append((branch, index))
            except ValueError:
                pass

        # Do we have something to do ?
        if len(deploys) == 0:
            raise SccsException(
                "continuous deployment seems not supported for {}".format(repository)
            )

        # Ordered deploys
        deploys = sorted(deploys, key=lambda deploy: deploy[1])

        # Get continuous deployment config for all environments selected
        tasks = []
        for branch, index in deploys:
            tasks.append(
                self._get_continuous_deployment_config_by_branch(
                    repository, repo, branch, self.cd_environments[index]
                )
            )

        task_results = await asyncio.gather(*tasks, return_exceptions=True)

        response = {}
        for [branch, results] in task_results:
            response[branch] = results

        results = [response[branch] for branch in response]
        logging.debug(
            f"_fetch_continuous_deployment_config for {repository} result is : {results}"
        )
        return results
