"""
Tests for FileSystemRepository.
"""

import tempfile
from pathlib import Path
import yaml

from repository import FileSystemRepository


class TestFileSystemRepository:
    """Test file system repository functionality."""

    def test_load_all_organizations_success(self):
        """Test loading organizations from a directory with valid YAML files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test YAML files
            org1_data = {"nazwa": "Org 1", "adres": "org-1"}
            org2_data = {"nazwa": "Org 2", "adres": "org-2"}

            org1_file = Path(temp_dir) / "org1.yaml"
            org2_file = Path(temp_dir) / "org2.yaml"

            with open(org1_file, "w") as f:
                yaml.dump(org1_data, f)
            with open(org2_file, "w") as f:
                yaml.dump(org2_data, f)

            repository = FileSystemRepository(temp_dir)
            organizations, errors = repository.load_all_organizations("adres")

            assert len(errors) == 0
            assert organizations == {
                "org-1": f"{temp_dir}/org1.yaml",
                "org-2": f"{temp_dir}/org2.yaml",
            }

    def test_load_all_organizations_duplicate_slugs(self):
        """Test detection of duplicate slugs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test YAML files with duplicate slug
            org1_data = {"nazwa": "Org 1", "adres": "duplicate"}
            org2_data = {"nazwa": "Org 2", "adres": "duplicate"}  # Same slug

            org1_file = Path(temp_dir) / "org1.yaml"
            org2_file = Path(temp_dir) / "org2.yaml"

            with open(org1_file, "w") as f:
                yaml.dump(org1_data, f)
            with open(org2_file, "w") as f:
                yaml.dump(org2_data, f)

            repository = FileSystemRepository(temp_dir)
            organizations, errors = repository.load_all_organizations("adres")

            assert len(errors) == 1
            assert "Duplikat adres 'duplicate'" in errors[0]
            assert "org1.yaml" in errors[0] and "org2.yaml" in errors[0]
            # Only one organization should be in the result (the last one processed)
            assert len(organizations) == 1

    def test_load_all_organizations_missing_slug_field(self):
        """Test handling files without the required slug field."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create YAML file without slug field
            org_data = {"nazwa": "Org Without Slug"}  # Missing "adres"

            org_file = Path(temp_dir) / "incomplete.yaml"
            with open(org_file, "w") as f:
                yaml.dump(org_data, f)

            repository = FileSystemRepository(temp_dir)
            organizations, errors = repository.load_all_organizations("adres")

            # File should be ignored (not an error, just not included)
            assert len(errors) == 0
            assert len(organizations) == 0

    def test_load_all_organizations_invalid_yaml(self):
        """Test handling files with invalid YAML syntax."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create file with invalid YAML
            invalid_file = Path(temp_dir) / "invalid.yaml"
            with open(invalid_file, "w") as f:
                f.write("invalid: yaml: content: [")  # Invalid syntax

            repository = FileSystemRepository(temp_dir)
            organizations, errors = repository.load_all_organizations("adres")

            assert len(errors) == 1
            assert "Błąd wczytywania pliku invalid.yaml" in errors[0]
            assert len(organizations) == 0

    def test_load_all_organizations_both_yaml_extensions(self):
        """Test loading both .yaml and .yml files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create files with both extensions
            org1_data = {"nazwa": "Org 1", "adres": "org-1"}
            org2_data = {"nazwa": "Org 2", "adres": "org-2"}

            yaml_file = Path(temp_dir) / "org1.yaml"
            yml_file = Path(temp_dir) / "org2.yml"

            with open(yaml_file, "w") as f:
                yaml.dump(org1_data, f)
            with open(yml_file, "w") as f:
                yaml.dump(org2_data, f)

            repository = FileSystemRepository(temp_dir)
            organizations, errors = repository.load_all_organizations("adres")

            assert len(errors) == 0
            assert len(organizations) == 2
            assert "org-1" in organizations
            assert "org-2" in organizations

    def test_load_all_organizations_nonexistent_directory(self):
        """Test handling nonexistent directory."""
        repository = FileSystemRepository("/nonexistent/directory")
        organizations, errors = repository.load_all_organizations("adres")

        assert len(errors) == 0
        assert len(organizations) == 0

    def test_load_organization_data_success(self):
        """Test loading individual organization data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            org_data = {
                "nazwa": "Test Org",
                "adres": "test-org",
                "strona": "https://test.org",
            }

            org_file = Path(temp_dir) / "test.yaml"
            with open(org_file, "w") as f:
                yaml.dump(org_data, f)

            repository = FileSystemRepository(temp_dir)
            loaded_data = repository.load_organization_data(str(org_file))

            assert loaded_data == org_data

    def test_load_organization_data_nonexistent_file(self):
        """Test loading data from nonexistent file."""
        repository = FileSystemRepository("/tmp")
        loaded_data = repository.load_organization_data("/nonexistent/file.yaml")

        assert loaded_data is None

    def test_load_organization_data_invalid_yaml(self):
        """Test loading data from file with invalid YAML."""
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_file = Path(temp_dir) / "invalid.yaml"
            with open(invalid_file, "w") as f:
                f.write("invalid: yaml: [")

            repository = FileSystemRepository(temp_dir)
            loaded_data = repository.load_organization_data(str(invalid_file))

            assert loaded_data is None

    def test_load_organization_data_empty_file(self):
        """Test loading data from empty YAML file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            empty_file = Path(temp_dir) / "empty.yaml"
            with open(empty_file, "w") as f:
                f.write("")  # Empty file

            repository = FileSystemRepository(temp_dir)
            loaded_data = repository.load_organization_data(str(empty_file))

            assert loaded_data is None

    def test_custom_slug_field(self):
        """Test using custom slug field name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            org_data = {"nazwa": "Test Org", "custom_slug": "test-slug"}

            org_file = Path(temp_dir) / "test.yaml"
            with open(org_file, "w") as f:
                yaml.dump(org_data, f)

            repository = FileSystemRepository(temp_dir)
            organizations, errors = repository.load_all_organizations("custom_slug")

            assert len(errors) == 0
            assert organizations == {"test-slug": f"{temp_dir}/test.yaml"}
