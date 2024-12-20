import logging
from dataclasses import dataclass

from github import InputGitTreeElement
from github.Commit import Commit
from github.GithubException import UnknownObjectException
from github.GitCommit import GitCommit
from github.GitRef import GitRef
from github.Issue import Issue
from github.PullRequest import PullRequest
from github.Repository import Repository

from consts import OrgFormSchemaIds
from exceptions import BranchModifiedError
from parsers import GithubIssueFormDataParser

logger = logging.getLogger(__file__)


@dataclass
class GitManager:
    """Manager for creating a new branch and pull request with a file commit in the repo."""

    repo: Repository

    def commit_file_contents_to_branch(
        self, branch_ref: GitRef, file_path: str, contents: str, commit_message: str
    ) -> GitCommit:
        latest_commit = self.repo.get_commit(branch_ref.object.sha)
        blob = self.repo.create_git_blob(contents, "utf-8")
        tree_element = InputGitTreeElement(
            path=file_path, mode="100644", type="blob", sha=blob.sha
        )
        base_tree = latest_commit.commit.tree
        new_tree = self.repo.create_git_tree([tree_element], base_tree)
        new_commit = self.repo.create_git_commit(
            message=commit_message, tree=new_tree, parents=[latest_commit.commit]
        )
        return new_commit

    def get_or_create_branch(self, source_branch: str, new_branch_name: str) -> GitRef:
        source = self.repo.get_branch(source_branch)
        try:
            branch_ref = self.repo.get_git_ref(f"heads/{new_branch_name}")
            logger.info(f"Found existing branch '{new_branch_name}'.")
        except UnknownObjectException:
            # Branch does not exist, create it from the source branch
            branch_ref = self.repo.create_git_ref(
                ref=f"refs/heads/{new_branch_name}", sha=source.commit.sha
            )
            logger.info(f"Branch '{new_branch_name}' created from '{source_branch}'.")

        latest_commit = self.repo.get_commit(branch_ref.object.sha)
        if (
            latest_commit.sha != source.commit.sha
            and not latest_commit.commit.message.startswith("[auto] ")
        ):
            logger.error(f"Branch was modified: {latest_commit.commit.message}")
            raise BranchModifiedError()

        return branch_ref

    def get_or_create_pr(
        self, target_branch: str, new_branch_name: str, pr_title: str, pr_body: str
    ) -> PullRequest:
        pulls = self.repo.get_pulls(
            state="open",
            head=f"{self.repo.owner.login}:{new_branch_name}",
            base=target_branch,
        )
        if pulls.totalCount > 0:
            logger.warning(
                f"Pull request already exists for branch '{new_branch_name}': {pulls[0].html_url}"
            )
            return pulls[0]

        logger.info(f"Creating pull request for branch '{new_branch_name}'")
        return self.repo.create_pull(
            title=pr_title, body=pr_body, head=new_branch_name, base=target_branch
        )

    def create_or_update_remote_branch_with_file_commit(
        self,
        source_branch: str,
        new_branch: str,
        file_path: str,
        file_contents: str,
        commit_message: str,
    ) -> GitRef:
        """Create or update a remote branch with a file commit."""
        branch = self.get_or_create_branch(source_branch, new_branch)
        commit = self.commit_file_contents_to_branch(
            branch, file_path, file_contents, commit_message
        )
        branch.edit(commit.sha)
        return branch

    def create_or_update_pr_with_file(
        self,
        source_branch: str,
        new_branch: str,
        pr_title: str,
        pr_body: str,
        file_path: str,
        file_contents: str,
        commit_message: str,
    ) -> PullRequest:
        self.create_or_update_remote_branch_with_file_commit(
            source_branch, new_branch, file_path, file_contents, commit_message
        )
        return self.get_or_create_pr(source_branch, new_branch, pr_title, pr_body)


def create_organization_yaml_pr(
    issue: Issue, yaml_string: str, data: GithubIssueFormDataParser
):
    repo = issue.repository

    source_branch = "main"
    new_branch_name = f"nowa-organizacja-zgloszenie-{issue.number}"

    commit_message = f"[auto] Dodana nowa organizacja: {data.get(OrgFormSchemaIds.name)} | Zgłoszenie: #{issue.number}"
    pr_title = f"Dodana nowa organizacja: {data.get(OrgFormSchemaIds.name)} | Zgłoszenie: #{issue.number}"
    pr_body = f"Automatycznie dodana nowa organizacja na podstawie zgłoszenia z issue #{issue.number}.\n\n Closes #{issue.number}"

    file_path = f"organizations/{data.get(OrgFormSchemaIds.slug)}.yaml"

    manager = GitManager(repo)
    manager.create_or_update_pr_with_file(
        source_branch=source_branch,
        new_branch=new_branch_name,
        pr_title=pr_title,
        pr_body=pr_body,
        file_path=file_path,
        file_contents=yaml_string,
        commit_message=commit_message,
    )
