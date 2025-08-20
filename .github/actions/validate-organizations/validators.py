"""
Focused validation components for organization data.
Each validator has a single responsibility and can be tested in isolation.
"""

import re
from typing import List, Tuple, Dict, Optional, Protocol
from krs_puller import KRSDataPuller, KRSMaintenanceError
import requests


class KRSClient(Protocol):
    """Protocol for KRS API client (allows mocking)."""

    def validate_krs(
        self, krs: str, expected_name: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Validate KRS number and optionally check name match."""
        pass


class RealKRSClient:
    """Real KRS client using the KRSDataPuller."""

    def validate_krs(
        self, krs: str, expected_name: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Validate KRS number against the registry and optionally check name match."""
        try:
            krs_data = KRSDataPuller(krs)

            if not krs_data.name:
                return (
                    False,
                    f"KRS {krs} istnieje, ale dane organizacji są niekompletne",
                )

            # Check name match if provided
            if expected_name:
                yaml_name = expected_name.strip()
                krs_name = krs_data.name.strip()

                if yaml_name.lower() != krs_name.lower():
                    return (
                        False,
                        f"Niezgodność nazwy organizacji: w YAML jest '{yaml_name}', ale w KRS jest '{krs_name}'",
                    )

            return True, ""

        except KRSMaintenanceError as e:
            # During maintenance, return warning but don't fail validation
            return True, f"⚠️ {e}"

        except requests.HTTPError:
            return (
                False,
                f"KRS {krs} nie zostało znalezione w rejestrze lub wystąpił błąd sieci",
            )


class OrganizationSchemaValidator:
    """Validates YAML structure and required fields."""

    def __init__(self, slug_field: str, krs_client: KRSClient):
        self.slug_field = slug_field
        self.krs_client = krs_client

    def validate_structure(self, data: dict) -> Tuple[bool, List[str]]:
        """Validate organization data structure and required fields."""
        errors = []

        if not data:
            errors.append("Pusty plik YAML")
            return False, errors

        # Required fields
        required_fields = [
            "nazwa",
            self.slug_field,
            "strona",
            "krs",
            "dostawa",
            "produkty",
        ]

        for field in required_fields:
            if field not in data:
                errors.append(f"Brakuje wymaganego pola: {field}")

        # Validate specific field formats
        if "krs" in data:
            krs = str(data["krs"])
            if not re.fullmatch(r"\d{10}", krs):
                errors.append(f"Nieprawidłowy format KRS: {krs} (oczekiwano 10 cyfr)")
            else:
                # Validate KRS against external API, including name match
                org_name = data.get("nazwa")
                is_valid, error_msg = self.krs_client.validate_krs(krs, org_name)
                if not is_valid:
                    errors.append(f"Walidacja KRS nie powiodła się: {error_msg}")
                elif error_msg:  # Warning message
                    print(f"  ⚠️  {error_msg}")

        if self.slug_field in data:
            slug = data[self.slug_field]
            if not isinstance(slug, str) or not slug.strip():
                errors.append(
                    f"Nieprawidłowy {self.slug_field}: musi być niepustym ciągiem znaków"
                )
            elif not re.fullmatch(r"[a-z0-9-]+", slug):
                errors.append(
                    f"Nieprawidłowy format {self.slug_field}: {slug} (dozwolone tylko małe litery, cyfry i myślniki)"
                )

        # Validate dostawa structure
        if "dostawa" in data:
            errors.extend(self._validate_delivery(data["dostawa"]))

        # Validate produkty structure
        if "produkty" in data and data["produkty"]:
            errors.extend(self._validate_products(data["produkty"]))

        return len(errors) == 0, errors

    def _validate_delivery(self, delivery: dict) -> List[str]:
        """Validate delivery data structure."""
        errors = []

        if not delivery or not isinstance(delivery, dict):
            errors.append("Pole dostawa musi być obiektem z wymaganymi polami")
            return errors

        required_delivery_fields = ["ulica", "kod", "miasto", "telefon"]
        for field in required_delivery_fields:
            if field not in delivery:
                errors.append(f"Brakuje wymaganego pola dostawy: dostawa.{field}")
            elif not delivery[field] or not str(delivery[field]).strip():
                errors.append(f"Pole dostawa.{field} nie może być puste")

        # Validate postal code format
        if "kod" in delivery and delivery["kod"]:
            postal_code = str(delivery["kod"])
            if not re.fullmatch(r"\d{2}-\d{3}", postal_code):
                errors.append(
                    f"Nieprawidłowy format kodu pocztowego: {postal_code} (oczekiwany format: 00-000)"
                )

        # Validate phone number
        if "telefon" in delivery and delivery["telefon"]:
            phone = re.sub(r"[\s-]", "", str(delivery["telefon"]))
            if not re.fullmatch(r"(\+?48|0048)?\d{9}", phone):
                errors.append(
                    f"Nieprawidłowy format numeru telefonu: {delivery['telefon']}"
                )

        return errors

    def _validate_products(self, products: list) -> List[str]:
        """Validate products list structure."""
        errors = []

        if not isinstance(products, list):
            errors.append("Pole produkty musi być listą")
            return errors

        for i, product in enumerate(products):
            if not isinstance(product, dict):
                errors.append(f"produkty[{i}] musi być obiektem")
                continue

            if "nazwa" not in product:
                errors.append(f"produkty[{i}] brakuje wymaganego pola: nazwa")
            elif not product["nazwa"] or not str(product["nazwa"]).strip():
                errors.append(f"produkty[{i}] pole nazwa nie może być puste")

            if "link" not in product:
                errors.append(f"produkty[{i}] brakuje wymaganego pola: link")
            elif not product["link"] or not str(product["link"]).strip():
                errors.append(f"produkty[{i}] pole link nie może być puste")

        return errors


class SlugConflictValidator:
    """Validates slug conflicts with reserved slugs."""

    def __init__(self, slug_field: str):
        self.slug_field = slug_field
        self.reserved_slugs = {"info", "organizacje", "404"}

    def validate_conflicts(
        self, files_to_check: List[str], all_organizations: Dict[str, str]
    ) -> Tuple[bool, List[str]]:
        """Check for slug conflicts with reserved slugs."""
        errors = []

        # Check reserved slug conflicts for files being checked
        for slug, filename in all_organizations.items():
            if filename in files_to_check and slug in self.reserved_slugs:
                errors.append(
                    f"Zarezerwowany {self.slug_field} '{slug}' używany w pliku {filename}"
                )

        return len(errors) == 0, errors
