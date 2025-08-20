import os
import re
from dataclasses import dataclass

import yaml
from github import Issue

from consts import OrgFormSchemaIds, ORG_SCHEMA_SLUG_FIELD
from labels import INVALID_FIELD_TO_LABEL
from parsers import GithubIssueFormDataParser
from utils import has_label


@dataclass
class OrgIssueValidator:
    data: GithubIssueFormDataParser
    issue: Issue

    def validate_krs(self) -> tuple[bool, str]:
        return (
            bool(re.fullmatch(r"\d{10}", self.data.get(OrgFormSchemaIds.krs))),
            "niepoprawny numer KRS",
        )

    def validate_postal_code(self) -> tuple[bool, str]:
        return (
            bool(
                re.fullmatch(
                    r"\d{2}-\d{3}", self.data.get(OrgFormSchemaIds.postal_code)
                )
            ),
            "niepoprawny kod pocztowy (oczekiwany format: 00-000)",
        )

    def validate_phone_number(self) -> tuple[bool, str]:
        return (
            bool(
                re.fullmatch(
                    r"(\+?48|0048)?\d{9}",
                    re.sub(r"[\s-]", "", self.data.get(OrgFormSchemaIds.phone_number)),
                )
            ),
            "niepoprawny numer telefonu",
        )

    def validate_slug(self) -> tuple[bool, str]:
        """
        Checks if any organization with the same slug already exists.
        """
        slug_value = self.data.get(OrgFormSchemaIds.slug)
        reserved_slugs = {
            "info",
            "organizacje",
        }

        for root, _, files in os.walk("../../organizations"):
            for file_name in files:
                with open(os.path.join(root, file_name), "r") as f:
                    org_data = yaml.safe_load(f)
                    if org_data[ORG_SCHEMA_SLUG_FIELD] == slug_value:
                        return (
                            False,
                            f"organizacja z adresem `/{slug_value}` już istnieje w `wyślij.co`. Proszę zmienić wartość na inną.",
                        )

        if slug_value in reserved_slugs:
            return (
                False,
                f"adres `/{slug_value}` jest zarezerwowany. Proszę zmienić wartość na inną.",
            )

        return True, ""

    def validate(self) -> bool:
        """
        Validates the organization data.

        :return: dict, a dictionary containing the validation results with keys being identifiers
        of the fields in the schema.
        """

        validation_map = {
            OrgFormSchemaIds.krs: self.validate_krs,
            OrgFormSchemaIds.postal_code: self.validate_postal_code,
            OrgFormSchemaIds.phone_number: self.validate_phone_number,
            OrgFormSchemaIds.slug: self.validate_slug,
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
                errors.append(
                    (
                        field,
                        msg,
                    )
                )

        if errors:
            msg = (
                "Wprowadzone dane są nieprawidłowe. Prosimy o wprowadzenie poprawek:\n"
            )
            for field, error in errors:
                msg += f"- **{self.data.get_label(field)}**: {error}\n"
            self.issue.create_comment(msg)
            return False

        return True
