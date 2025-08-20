"""
Integration tests for the complete validation system.
"""

from io import StringIO
import sys

from validate import OrganizationValidator


class TestIntegrationValidation:
    """Test complete validation workflow."""

    def test_complete_validation_success(
        self, mock_repository, mock_krs_client, valid_organization_data
    ):
        """Test complete validation workflow with valid data."""
        # Setup mock data
        mock_repository.set_organizations({"test-foundation": "test.yaml"})
        mock_repository.set_file_data("test.yaml", valid_organization_data)
        mock_krs_client.set_response("1234567890", True, "")

        # Create validator with mocked dependencies
        validator = OrganizationValidator(mock_repository, "adres")
        validator.schema_validator.krs_client = mock_krs_client

        # Capture output
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            result = validator.validate_files(["test.yaml"])

            assert result is True

            output = captured_output.getvalue()
            assert "🚀 Rozpoczynam walidację organizacji" in output
            assert "✅ Walidacja struktury zakończona pomyślnie" in output
            assert "✅ Nie znaleziono konfliktów adresów" in output
            assert "🎉 Wszystkie walidacje zakończone pomyślnie!" in output

        finally:
            sys.stdout = sys.__stdout__

    def test_complete_validation_with_errors(self, mock_repository, mock_krs_client):
        """Test complete validation workflow with validation errors."""
        invalid_data = {
            "nazwa": "",  # Invalid empty name
            "adres": "info",  # Reserved slug
            "krs": "123",  # Invalid KRS format
            # Missing required fields
        }

        # Setup mock data
        mock_repository.set_organizations({"info": "invalid.yaml"})
        mock_repository.set_file_data("invalid.yaml", invalid_data)
        mock_krs_client.set_default_response(False, "KRS validation failed")

        # Create validator with mocked dependencies
        validator = OrganizationValidator(mock_repository, "adres")
        validator.schema_validator.krs_client = mock_krs_client

        # Capture output
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            result = validator.validate_files(["invalid.yaml"])

            assert result is False

            output = captured_output.getvalue()
            assert "❌ Walidacja struktury nie powiodła się" in output
            assert "❌ Znaleziono konflikty adresów" in output
            assert "💥 Walidacja nie powiodła się!" in output

        finally:
            sys.stdout = sys.__stdout__

    def test_validation_with_loading_errors(self, mock_repository, mock_krs_client):
        """Test validation with organization loading errors."""
        # Setup mock data with loading errors
        mock_repository.set_load_errors(
            ["Błąd wczytywania pliku test.yaml: Invalid syntax"]
        )

        validator = OrganizationValidator(mock_repository, "adres")
        validator.schema_validator.krs_client = mock_krs_client

        # Capture output
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            result = validator.validate_files(["test.yaml"])

            assert result is False

            output = captured_output.getvalue()
            assert "❌ Krytyczne błędy wczytywania organizacji" in output
            assert "Invalid syntax" in output

        finally:
            sys.stdout = sys.__stdout__

    def test_validation_with_missing_file(self, mock_repository, mock_krs_client):
        """Test validation with missing file."""
        # Setup mock without file data
        mock_repository.set_organizations({})

        validator = OrganizationValidator(mock_repository, "adres")
        validator.schema_validator.krs_client = mock_krs_client

        # Capture output
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            result = validator.validate_files(["missing.yaml"])

            assert result is False

            output = captured_output.getvalue()
            assert "❌ Plik nie znaleziony lub nie można go odczytać" in output

        finally:
            sys.stdout = sys.__stdout__

    def test_validation_with_krs_warning(
        self, mock_repository, mock_krs_client, valid_organization_data
    ):
        """Test validation with KRS maintenance warning."""
        # Setup mock data
        mock_repository.set_organizations({"test-foundation": "test.yaml"})
        mock_repository.set_file_data("test.yaml", valid_organization_data)
        mock_krs_client.set_response("1234567890", True, "⚠️ Maintenance mode")

        validator = OrganizationValidator(mock_repository, "adres")
        validator.schema_validator.krs_client = mock_krs_client

        # Capture output
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            result = validator.validate_files(["test.yaml"])

            assert result is True  # Should pass despite warning

            output = captured_output.getvalue()
            assert "⚠️" in output
            assert "Maintenance mode" in output

        finally:
            sys.stdout = sys.__stdout__

    def test_validation_multiple_files(
        self, mock_repository, mock_krs_client, valid_organization_data
    ):
        """Test validation with multiple files."""
        # Setup multiple valid organizations
        org1_data = valid_organization_data.copy()
        org1_data["adres"] = "org-1"

        org2_data = valid_organization_data.copy()
        org2_data["adres"] = "org-2"
        org2_data["krs"] = "0987654321"

        mock_repository.set_organizations({"org-1": "org1.yaml", "org-2": "org2.yaml"})
        mock_repository.set_file_data("org1.yaml", org1_data)
        mock_repository.set_file_data("org2.yaml", org2_data)

        mock_krs_client.set_response("1234567890", True, "")
        mock_krs_client.set_response("0987654321", True, "")

        validator = OrganizationValidator(mock_repository, "adres")
        validator.schema_validator.krs_client = mock_krs_client

        # Capture output
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            result = validator.validate_files(["org1.yaml", "org2.yaml"])

            assert result is True

            output = captured_output.getvalue()
            assert "Walidacja 2 pliku/ów organizacji" in output
            assert "Walidacja org1.yaml" in output
            assert "Walidacja org2.yaml" in output

        finally:
            sys.stdout = sys.__stdout__

    def test_validation_mixed_results(
        self, mock_repository, mock_krs_client, valid_organization_data
    ):
        """Test validation with mixed valid and invalid files."""
        # One valid, one invalid organization
        invalid_data = {
            "nazwa": "Invalid Org",
            "adres": "info",  # Reserved slug
            "krs": "1111111111",
        }

        mock_repository.set_organizations(
            {"test-foundation": "valid.yaml", "info": "invalid.yaml"}
        )
        mock_repository.set_file_data("valid.yaml", valid_organization_data)
        mock_repository.set_file_data("invalid.yaml", invalid_data)

        mock_krs_client.set_response("1234567890", True, "")
        mock_krs_client.set_response("1111111111", True, "")

        validator = OrganizationValidator(mock_repository, "adres")
        validator.schema_validator.krs_client = mock_krs_client

        # Capture output
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            result = validator.validate_files(["valid.yaml", "invalid.yaml"])

            assert result is False  # Should fail due to invalid file

            output = captured_output.getvalue()
            assert (
                "✅ Walidacja struktury zakończona pomyślnie" in output
            )  # For valid file
            assert (
                "❌ Walidacja struktury nie powiodła się" in output
            )  # For invalid file
            assert "❌ Znaleziono konflikty adresów" in output  # Reserved slug conflict

        finally:
            sys.stdout = sys.__stdout__
