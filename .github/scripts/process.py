import json
import logging
import os

from github import Auth, Github, Issue

from label import Label
from parsers import FormDataParser
from pullers import OrgDataPuller
from utils import has_label

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__file__)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

auth = Auth.Token(GITHUB_TOKEN)
g = Github(auth=auth)
repo = g.get_repo("ivellios/wyslijco.github.io")


def process_new_org_issue(issue: Issue, data: FormDataParser):
    if not (org := OrgDataPuller.get_org_by_krs(issue, data.get("krs"))):
        if has_label(issue, Label.AUTO_VERIFIED):
            issue.remove_from_labels(Label.AUTO_VERIFIED)
        return

    # Update issue title
    if issue.title == "[Nowa Organizacja]":
        logger.info("Updating issue title")
        issue.edit(title=f"[Nowa Organizacja] {org.name or data.get('nazwa')}")

    if not has_label(issue, Label.AUTO_VERIFIED):
        issue.create_comment(f"@{issue.user.login}, dziękujemy za podanie informacji. "
                             f"Przyjęliśmy zgłoszenie dodania nowej organizacji. "
                             f"Wkrótce skontaktujemy się celem weryfikacji zgłoszenia.")
        issue.add_to_labels(Label.AUTO_VERIFIED)


def main():
    github_form_json = os.getenv("GITHUB_FORM_JSON")
    github_issue_number = int(os.getenv("GITHUB_ISSUE_NUMBER"))
    form_schema_filename = "nowa.yaml"

    issue = repo.get_issue(github_issue_number)
    data = FormDataParser(
        json.loads(github_form_json),
        form_schema_filename
    )
    process_new_org_issue(issue, data)


if __name__ == "__main__":
    main()
