import enum


class OrgSchemaIds(enum.StrEnum):
    name = "nazwa"
    www = "www"
    krs = "krs"
    slug = "nazwa_strony"
    street = "ulica"
    postal_code = "kod_pocztowy"
    city = "miasto"
    phone_number = "telefon"

NEW_ORG_ISSUE_DEFAULT_TITLE = "[Nowa Organizacja]"
NEW_ORG_SCHEMA_FILENAME = "nowa.yaml"


ORG_SCHEMA_SLUG_FIELD = "adres"
