import re

from github import Issue

from consts import OrgSchemaIds
from parsers import FormDataParser


class OrgValidator:

    def __init__(self, data: FormDataParser):
        self.data = data

    def validate_krs(self):
        return bool(re.fullmatch(r"\d{10}", self.data.get(OrgSchemaIds.krs)))

    def validate_postal_code(self) -> bool:
        return bool(
            re.fullmatch(r"\d{2}-\d{3}", self.data.get(OrgSchemaIds.postal_code))
        )

    def validate_phone_number(self) -> bool:
        return bool(
            re.fullmatch(
                r"(\+?48|0048)?\d{9}",
                re.sub(r"[\s-]", "", self.data.get(OrgSchemaIds.phone_number))
            )
        )

    def validate(self) -> dict[str, bool]:
        """
        Validates the organization data.

        :return: dict, a dictionary containing the validation results with keys being identifiers
        of the fields in the schema.
        """

        return {
            OrgSchemaIds.krs: self.validate_krs(),
            OrgSchemaIds.postal_code: self.validate_postal_code(),
            OrgSchemaIds.phone_number: self.validate_phone_number()
        }
