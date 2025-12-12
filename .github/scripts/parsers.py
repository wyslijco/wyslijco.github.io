from typing import Any

import yaml


class GithubIssueFormDataParser:
    """
    Parses data comming from a Github issue form converted
    to a dictionary and provides methods to access the data
    """

    def __init__(
        self,
        form_data: dict[str, Any],
        form_schema_filename: str,
        extra_labels_map: dict[str, str],
    ):
        self.form_data = form_data
        self.form_schema_filename = form_schema_filename
        self.form_schema = self.get_form_schema(form_schema_filename)

        self.extra_labels_map = extra_labels_map
        self.field_label_map = self._create_field_label_map()

    def _create_field_label_map(self):
        field_label_map = {}
        for field in self.form_schema.get("body", []):
            if "id" in field:
                field_label_map[field["id"]] = field["attributes"]["label"]

        for identifier, label in self.extra_labels_map.items():
            field_label_map[identifier] = label

        return field_label_map

    @staticmethod
    def get_form_schema(template_filename):
        with open(f"../ISSUE_TEMPLATE/{template_filename}") as f:
            return yaml.safe_load(f)

    def get_label(self, identifier: str) -> str | None:
        return self.field_label_map.get(identifier)

    def get(self, identifier: str) -> str | None:
        label = self.get_label(identifier)
        value = self.form_data.get(label, "")
        if value == "_No response_":
            return ""
        return value

    def set(self, name: str, value):
        self.form_data[self.get_label(name)] = value
