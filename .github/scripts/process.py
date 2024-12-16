import json
import logging
import os

from github import Auth, Github, Issue

from consts import OrgSchemaIds, NEW_ORG_ISSUE_DEFAULT_TITLE, NEW_ORG_SCHEMA_FILENAME
from labels import Label, INVALID_FIELD_TO_LABEL
from parsers import FormDataParser
from pullers import OrgDataPuller
from utils import has_label
from validators import OrgValidator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__file__)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")

auth = Auth.Token(GITHUB_TOKEN)
g = Github(auth=auth)
repo = g.get_repo(GITHUB_REPOSITORY)


def process_new_org_issue(issue: Issue, data: FormDataParser):
    if has_label(issue, Label.AUTO_VERIFIED):
        issue.remove_from_labels(Label.AUTO_VERIFIED)

    validator = OrgValidator(data)
    validation_results = validator.validate()

    if not all(validation_results.values()):
        for field, is_valid in validation_results.items():
            if not is_valid:
                issue.add_to_labels(INVALID_FIELD_TO_LABEL[field])

        invalid_fields_text = ", ".join([data.get_label(field) for field, is_valid in validation_results.items() if not is_valid])
        issue.create_comment(f"Wprowadzone dane są nieprawidłowe. Prosimy poprawić: {invalid_fields_text}")
        return
    else:
        # Make sure to remove invalid labels if their values have been corrected
        for field in validation_results.keys():
            if has_label(issue, INVALID_FIELD_TO_LABEL[field]):
                issue.remove_from_labels(INVALID_FIELD_TO_LABEL[field])

    if not (org := OrgDataPuller.get_org_by_krs(issue, data.get(OrgSchemaIds.krs))):
        return

    # Update issue title
    if issue.title == NEW_ORG_ISSUE_DEFAULT_TITLE:
        logger.info("Updating issue title")
        issue.edit(title=f"{NEW_ORG_ISSUE_DEFAULT_TITLE} {org.name or data.get(OrgSchemaIds.name)}")

    if not has_label(issue, Label.AUTO_VERIFIED):
        issue.create_comment(f"@{issue.user.login}, dziękujemy za podanie informacji. "
                             f"Przyjęliśmy zgłoszenie dodania nowej organizacji. "
                             f"Wkrótce skontaktujemy się celem weryfikacji zgłoszenia.")
        issue.add_to_labels(Label.AUTO_VERIFIED)


def main():
    github_form_json = os.getenv("GITHUB_FORM_JSON")
    github_issue_number = int(os.getenv("GITHUB_ISSUE_NUMBER"))

    issue = repo.get_issue(github_issue_number)
    data = FormDataParser(
        json.loads(github_form_json),
        NEW_ORG_SCHEMA_FILENAME
    )
    process_new_org_issue(issue, data)


if __name__ == "__main__":
    main()
