import yaml


class FormDataParser:

    def __init__(self, form_data, form_schema_filename):
        self.form_data = form_data
        self.form_schema_filename = form_schema_filename
        self.form_schema = self.get_form_schema(form_schema_filename)

    @staticmethod
    def get_form_schema(template_filename):
        with open(f"../ISSUE_TEMPLATE/{template_filename}") as f:
            return yaml.safe_load(f)

    def get_form_label(self, identifier: str) -> str | None:
        for field in self.form_schema.get("body", []):
            if "id" in field and field["id"] == identifier:
                return field["attributes"]["label"]
        return None

    def get(self, identifier: str) -> str | None:
        label = self.get_form_label(identifier)
        return self.form_data.get(label)
