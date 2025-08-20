#!/usr/bin/env python3
"""
Validation script for organization YAML files in GitHub Actions.
Validates organization files for schema compliance and slug conflicts.
"""

import sys
from typing import List

import click
from repository import FileSystemRepository
from validators import OrganizationSchemaValidator, SlugConflictValidator, RealKRSClient


class OrganizationValidator:
    """Orchestrates organization validation using injected dependencies."""

    def __init__(self, repository: FileSystemRepository, slug_field: str):
        self.repository = repository
        self.slug_field = slug_field

        # Initialize focused validators
        krs_client = RealKRSClient()
        self.schema_validator = OrganizationSchemaValidator(slug_field, krs_client)
        self.slug_validator = SlugConflictValidator(slug_field)

    def validate_files(self, files_to_check: List[str]) -> bool:
        """Validate a list of organization files."""

        print("=================================================")
        print("🚀 Rozpoczynam walidację organizacji...")

        # Load all organizations and check for duplicate slugs
        all_organizations, load_errors = self.repository.load_all_organizations(
            self.slug_field
        )

        if load_errors:
            print("❌ Krytyczne błędy wczytywania organizacji:")
            for error in load_errors:
                print(f"     - {error}")
            print("💥 Walidacja nie powiodła się!")
            return False

        print(f"Walidacja {len(files_to_check)} pliku/ów organizacji...")
        print(f"Pole {self.slug_field}: {self.slug_field}")
        print(
            f"Zarezerwowane adresy stron: {', '.join(sorted(self.slug_validator.reserved_slugs))}"
        )
        print()

        all_valid = True

        # Validate individual file structures
        for file_path in files_to_check:
            print(f"Walidacja {file_path}...")

            data = self.repository.load_organization_data(file_path)
            if not data:
                print(
                    f"  ❌ Plik nie znaleziony lub nie można go odczytać: {file_path}"
                )
                all_valid = False
                continue

            is_valid, errors = self.schema_validator.validate_structure(data)

            if is_valid:
                print("  ✅ Walidacja struktury zakończona pomyślnie")
            else:
                print("  ❌ Walidacja struktury nie powiodła się:")
                for error in errors:
                    print(f"     - {error}")
                all_valid = False

        print()

        # Check slug conflicts
        print("Sprawdzanie konfliktów adresów...")
        is_valid, errors = self.slug_validator.validate_conflicts(
            files_to_check, all_organizations
        )

        if is_valid:
            print("  ✅ Nie znaleziono konfliktów adresów")
        else:
            print("  ❌ Znaleziono konflikty adresów:")
            for error in errors:
                print(f"     - {error}")
            all_valid = False

        print()

        if all_valid:
            print("🎉 Wszystkie walidacje zakończone pomyślnie!")
        else:
            print("💥 Walidacja nie powiodła się!")

        print("=================================================")

        return all_valid


@click.command()
@click.option(
    "--files",
    required=True,
    help="Space-separated list of organization YAML files to validate",
)
@click.option(
    "--organizations-dir",
    default="organizations",
    help="Directory containing organization YAML files",
)
@click.option(
    "--slug-field", default="adres", help="YAML field name for organization slug"
)
def main(files: str, organizations_dir: str, slug_field: str):
    """Validate organization YAML files."""

    # Parse files list
    files_list = [f.strip() for f in files.split() if f.strip()]

    if not files_list:
        print("Brak plików do walidacji")
        sys.exit(0)

    # Create repository and validator
    repository = FileSystemRepository(organizations_dir)
    validator = OrganizationValidator(repository, slug_field)

    if validator.validate_files(files_list):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
