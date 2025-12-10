from dataclasses import dataclass
import os

import yaml

from config import (
    ORGANIZATIONS_DIR_PATH,
    ORGANIZATIONS_SLUG_FIELD_NAME,
    ORGANIZATIONS_NAME_FIELD_NAME,
)


def trim_strings(data):
    """Recursively trim trailing/leading spaces from all string values in nested data structures."""
    if isinstance(data, dict):
        return {key: trim_strings(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [trim_strings(item) for item in data]
    elif isinstance(data, str):
        return data.strip()
    else:
        return data


@dataclass
class Organization:
    file: str
    name: str
    slugs: list[str]


def get_organizations() -> tuple[dict[str, Organization], dict[str, Organization]]:
    organization_files = filter(
        lambda x: x.endswith(".yaml"), os.listdir(ORGANIZATIONS_DIR_PATH)
    )
    organizations = dict()
    slugs_map = dict()
    for organization_file in organization_files:
        with open(f"{ORGANIZATIONS_DIR_PATH}/{organization_file}") as org:
            organization_data = trim_strings(yaml.safe_load(org))
            slug_field_value = organization_data.get(ORGANIZATIONS_SLUG_FIELD_NAME)
            slugs = (
                slug_field_value
                if isinstance(slug_field_value, list)
                else [slug_field_value]
            )
            organization = Organization(
                file=organization_file,
                name=organization_data.get(ORGANIZATIONS_NAME_FIELD_NAME),
                slugs=slugs,
            )
            organizations[organization_file] = organization
            slugs_map.update({slug: organization for slug in slugs})
    return organizations, slugs_map


def get_organization_data(org: Organization):
    with open(f"{ORGANIZATIONS_DIR_PATH}/{org.file}") as org_file:
        data = trim_strings(yaml.safe_load(org_file))
        data[ORGANIZATIONS_SLUG_FIELD_NAME] = org.slugs[0]
        if not data["produkty"]:
            data["produkty"] = []
    return data
