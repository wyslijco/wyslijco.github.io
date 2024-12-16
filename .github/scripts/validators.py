import os
import re

import yaml
from github import Issue

from consts import OrgSchemaIds, ORG_SCHEMA_SLUG_FIELD
from labels import INVALID_FIELD_TO_LABEL, Label
from parsers import FormDataParser
from utils import has_label


class OrgValidator:

    def __init__(self, data: FormDataParser, issue: Issue):
        self.data = data
        self.issue = issue

    def validate_krs(self) -> tuple[bool, str]:
        return bool(re.fullmatch(r"\d{10}", self.data.get(OrgSchemaIds.krs))), "niepoprawny numer KRS"

    def validate_postal_code(self) -> tuple[bool, str]:
        return bool(
            re.fullmatch(r"\d{2}-\d{3}", self.data.get(OrgSchemaIds.postal_code))
        ), "niepoprawny kod pocztowy"

    def validate_phone_number(self) -> tuple[bool, str]:
        return bool(
            re.fullmatch(
                r"(\+?48|0048)?\d{9}",
                re.sub(r"[\s-]", "", self.data.get(OrgSchemaIds.phone_number))
            )
        ), "niepoprawny numer telefonu"

    def validate_slug(self) -> tuple[bool, str]:
        """
        Checks if any organization with the same slug already exists.
        """
        slug_value = self.data.get(OrgSchemaIds.slug)

        for root, _, files in os.walk("../../organizations"):
            for file_name in files:
                with open(os.path.join(root, file_name), "r") as f:
                    org_data = yaml.safe_load(f)
                    if org_data[ORG_SCHEMA_SLUG_FIELD] == slug_value:
                        return False, f"organizacja z adresem `/{slug_value}` już istnieje w `wyślij.co`. Proszę zmienić wartość na inną."

        return True, ""

    def validate(self) -> dict[str, bool]:
        """
        Validates the organization data.

        :return: dict, a dictionary containing the validation results with keys being identifiers
        of the fields in the schema.
        """

        validation_map = {
            OrgSchemaIds.krs: self.validate_krs,
            OrgSchemaIds.postal_code: self.validate_postal_code,
            OrgSchemaIds.phone_number: self.validate_phone_number,
            OrgSchemaIds.slug: self.validate_slug,
        }

        errors = []
        for field, validator in validation_map.items():
            result, msg = validator()
            label = INVALID_FIELD_TO_LABEL[field]
            if result:
                if has_label(self.issue, label):
                    self.issue.remove_from_labels(label)
            else:
                self.issue.add_to_labels(label)
                errors.append((field, msg,))

        if errors:
            msg = "Wprowadzone dane są nieprawidłowe. Prosimy o wprowadzenie poprawek:\n"
            for field, error in errors:
                msg += f"- **{self.data.get_label(field)}**: {error}\n"
            self.issue.create_comment(msg)
