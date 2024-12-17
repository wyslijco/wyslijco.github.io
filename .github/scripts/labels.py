import enum

from consts import OrgSchemaIds


class Label(enum.StrEnum):
    INVALID_KRS = "niepoprawny KRS"
    INVALID_POSTAL_CODE = "niepoprawny kod pocztowy"
    INVALID_PHONE = "niepoprawny numer telefonu"
    INVALID_SLUG = "niepoprawna nazwa strony"
    AUTO_VERIFIED = "zweryfikowana automatycznie"


INVALID_FIELD_TO_LABEL = {
    OrgSchemaIds.krs: Label.INVALID_KRS,
    OrgSchemaIds.postal_code: Label.INVALID_POSTAL_CODE,
    OrgSchemaIds.phone_number: Label.INVALID_PHONE,
    OrgSchemaIds.slug: Label.INVALID_SLUG,
}
