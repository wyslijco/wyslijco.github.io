import enum

from consts import OrgFormSchemaIds


class Label(enum.StrEnum):
    INVALID_KRS = "niepoprawny KRS"
    INVALID_POSTAL_CODE = "niepoprawny kod pocztowy"
    INVALID_PHONE = "niepoprawny numer telefonu"
    INVALID_SLUG = "niepoprawna nazwa strony"
    AUTO_VERIFIED = "zweryfikowana automatycznie"
    WAITING = "oczekuje na akceptację"


INVALID_FIELD_TO_LABEL = {
    OrgFormSchemaIds.krs: Label.INVALID_KRS,
    OrgFormSchemaIds.postal_code: Label.INVALID_POSTAL_CODE,
    OrgFormSchemaIds.phone_number: Label.INVALID_PHONE,
    OrgFormSchemaIds.slug: Label.INVALID_SLUG,
}
