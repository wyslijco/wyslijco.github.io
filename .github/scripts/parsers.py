from typing import Any

import yaml


class GithubIssueFormDataParser:
    """
    Parses data comming from a Github issue form converted
    to a dictionary and provides methods to access the data
    """

    def __init__(self, form_data: dict[str, Any], form_schema_filename: str):
        self.form_data = form_data
        self.form_schema_filename = form_schema_filename
        self.form_schema = self.get_form_schema(form_schema_filename)

    @staticmethod
    def get_form_schema(template_filename):
        with open(f"../ISSUE_TEMPLATE/{template_filename}") as f:
            return yaml.safe_load(f)

    def get_label(self, identifier: str) -> str | None:
        for field in self.form_schema.get("body", []):
            if "id" in field and field["id"] == identifier:
                return field["attributes"]["label"]
        return None

    def get(self, identifier: str) -> str | None:
        label = self.get_label(identifier)
        value = self.form_data.get(label, "")
        if value == "_No response_":
            return ""
        return value
