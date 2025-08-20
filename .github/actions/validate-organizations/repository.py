"""
Repository pattern for organization data access.
Separates file I/O from validation logic for better testability.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import yaml


class OrganizationRepository(ABC):
    """Abstract repository for organization data access."""

    @abstractmethod
    def load_all_organizations(
        self, slug_field: str
    ) -> Tuple[Dict[str, str], List[str]]:
        """
        Load all organizations and return slug to filename mapping with errors.

        Args:
            slug_field: YAML field name for organization slug

        Returns:
            Tuple of (slug_to_filename_mapping, errors)
        """
        pass

    @abstractmethod
    def load_organization_data(self, file_path: str) -> Optional[dict]:
        """
        Load organization data from a specific file.

        Args:
            file_path: Path to the organization file

        Returns:
            Organization data dictionary or None if failed
        """
        pass


class FileSystemRepository(OrganizationRepository):
    """File system implementation of organization repository."""

    def __init__(self, organizations_dir: str):
        self.organizations_dir = Path(organizations_dir)
        self.reserved_slugs = {"info", "organizacje", "404"}

    def load_all_organizations(
        self, slug_field: str
    ) -> Tuple[Dict[str, str], List[str]]:
        """Load all organization files and return slug to filename mapping with errors."""
        slug_to_file = {}
        errors = []

        if not self.organizations_dir.exists():
            return slug_to_file, errors

        yaml_files = list(self.organizations_dir.glob("*.yaml")) + list(
            self.organizations_dir.glob("*.yml")
        )
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data and slug_field in data:
                        slug = data[slug_field]
                        if slug in slug_to_file:
                            errors.append(
                                f"Duplikat {slug_field} '{slug}' znaleziony w {yaml_file.name} i {slug_to_file[slug]}"
                            )
                        else:
                            slug_to_file[slug] = str(
                                self.organizations_dir / yaml_file.name
                            )
            except Exception as e:
                errors.append(f"Błąd wczytywania pliku {yaml_file.name}: {e}")

        return slug_to_file, errors

    def load_organization_data(self, file_path: str) -> Optional[dict]:
        """Load organization data from a specific file."""
        try:
            full_path = Path(file_path)
            if not full_path.exists():
                return None

            with open(full_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception:
            return None
