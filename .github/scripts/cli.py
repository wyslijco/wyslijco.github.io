import json
import logging
import os

import click
from github import Auth, Github, Issue

from adapters import ProductsAdapter
from consts import (
    OrgFormSchemaIds,
    NEW_ORG_ISSUE_DEFAULT_TITLE,
    NEW_ORG_FORM_SCHEMA_FILENAME,
)
from exceptions import BranchModifiedError
from git_managers import create_organization_yaml_pr
from labels import Label
from parsers import GithubIssueFormDataParser
from pullers import KRSDataPuller
from utils import has_label
from validators import OrgIssueValidator
from renderers import render_organization_yaml

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__file__)

GITHUB_TOKEN = os.getenv("GITHUB_PAT")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")

auth = Auth.Token(GITHUB_TOKEN)
g = Github(auth=auth)
repo = g.get_repo(GITHUB_REPOSITORY)


@click.command()
@click.option(
    "--github-form-json",
    envvar="GITHUB_FORM_JSON",
    required=True,
    help="GitHub form JSON data",
)
@click.option(
    "--github-issue-number",
    envvar="GITHUB_ISSUE_NUMBER",
    type=int,
    required=True,
    help="GitHub issue number",
)
def process_new_org_issue(github_form_json, github_issue_number):
    issue: Issue = repo.get_issue(github_issue_number)
    data = GithubIssueFormDataParser(
        json.loads(github_form_json), NEW_ORG_FORM_SCHEMA_FILENAME
    )

    validation_warnings = []

    org_name = data.get(OrgFormSchemaIds.name)

    if has_label(issue, Label.AUTO_VERIFIED):
        issue.remove_from_labels(Label.AUTO_VERIFIED)

    validator = OrgIssueValidator(data, issue)
    if not validator.validate():
        logger.error("Validation failed - not continuing")
        return

    if not (
        krs_org := KRSDataPuller.get_org_by_krs(
            issue, krs=data.get(OrgFormSchemaIds.krs)
        )
    ):
        logger.error(msg="KRS db validation failed")
        validation_warnings.append("Nie można zweryfikować KRS")
    else:
        data[OrgFormSchemaIds.krs_name] = krs_org.name

    products_adapter = ProductsAdapter(data.get(OrgFormSchemaIds.products))
    data[OrgFormSchemaIds.products] = products_adapter.products

    # Update issue title
    if issue.title == NEW_ORG_ISSUE_DEFAULT_TITLE:
        logger.info("Updating issue title")
        issue.edit(title=f"{NEW_ORG_ISSUE_DEFAULT_TITLE} {org_name}")

    logger.info("Adding auto-verified label")
    if not validation_warnings:
        issue.add_to_labels(Label.AUTO_VERIFIED)

        if not has_label(issue, Label.WAITING):
            issue.add_to_labels(Label.WAITING)
            issue.create_comment(
                f"@{issue.user.login}, dziękujemy za podanie informacji. "
                "Przyjęliśmy zgłoszenie dodania nowej organizacji. \n\n"
                "Bardzo poważnie podchodzimy do weryfikacji "
                "wszystkich zgłoszonych organizacji oraz ich danych. \n\n"
                "W celu weryfikacji poprawności danych skontaktujemy się z Twoją organizacją "
                "poprzez oficjalne dane kontaktowe dostępne na stronie internetowej organizacji "
                "lub w rejestrze KRS. \n\n"
                "W przypadku pozytywnej weryfikacji, otrzymasz od nas informację o dalszych krokach."
            )

    # create organization yaml file and add to the Pull Request
    yaml_string = render_organization_yaml(data)

    try:
        create_organization_yaml_pr(issue, yaml_string, data)
    except BranchModifiedError:
        logger.error("Branch was modified by someone else")
        issue.create_comment(
            "Aktualizacja pliku organizacji na podstawie opisu zgłoszenia niemożliwa. "
            "Plik organizacji został już zmodyfikowany przez innego użytkownika."
        )


if __name__ == "__main__":
    process_new_org_issue()
