import enum


class OrgFormSchemaIds(enum.StrEnum):
    name = "name"
    website = "website"
    krs = "krs"
    krs_name = "krs_name"
    slug = "slug"
    street = "street"
    postal_code = "postal_code"
    city = "city"
    phone_number = "phone_number"
    email = "email"
    package_box_code = "package_box_code"
    additional_info = "additional_info"
    products = "products"


NEW_ORG_ISSUE_DEFAULT_TITLE = "[Nowa Organizacja]"
NEW_ORG_FORM_SCHEMA_FILENAME = "nowa.yaml"

EXTRA_LABELS_MAP = {"Nazwa w KRS": OrgFormSchemaIds.krs_name}


ORG_SCHEMA_SLUG_FIELD = "adres"
