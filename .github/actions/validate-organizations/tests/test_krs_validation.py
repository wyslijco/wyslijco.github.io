"""
Tests for KRS validation functionality.
"""

import responses
import requests

from validators import RealKRSClient, OrganizationSchemaValidator


class TestRealKRSClient:
    """Test the real KRS client with mocked HTTP responses."""

    @responses.activate
    def test_valid_krs_with_matching_name(self):
        """Test valid KRS with matching organization name."""
        krs = "1234567890"
        expected_name = "Test Foundation"

        # Mock successful KRS API response
        mock_response = {
            "odpis": {
                "dane": {"dzial1": {"danePodmiotu": {"nazwa": "Test Foundation"}}}
            }
        }

        responses.add(
            responses.GET,
            f"https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/{krs}?rejestr=S&format=json",
            json=mock_response,
            status=200,
        )

        client = RealKRSClient()
        is_valid, message = client.validate_krs(krs, expected_name)

        assert is_valid
        assert message == ""

    @responses.activate
    def test_valid_krs_with_mismatched_name(self):
        """Test valid KRS with mismatched organization name."""
        krs = "1234567890"
        expected_name = "Wrong Foundation"

        # Mock successful KRS API response with different name
        mock_response = {
            "odpis": {
                "dane": {"dzial1": {"danePodmiotu": {"nazwa": "Correct Foundation"}}}
            }
        }

        responses.add(
            responses.GET,
            f"https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/{krs}?rejestr=S&format=json",
            json=mock_response,
            status=200,
        )

        client = RealKRSClient()
        is_valid, message = client.validate_krs(krs, expected_name)

        assert not is_valid
        assert "Niezgodność nazwy organizacji" in message
        assert "Wrong Foundation" in message
        assert "Correct Foundation" in message

    @responses.activate
    def test_valid_krs_without_name_check(self):
        """Test valid KRS without name verification."""
        krs = "1234567890"

        # Mock successful KRS API response
        mock_response = {
            "odpis": {"dane": {"dzial1": {"danePodmiotu": {"nazwa": "Any Foundation"}}}}
        }

        responses.add(
            responses.GET,
            f"https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/{krs}?rejestr=S&format=json",
            json=mock_response,
            status=200,
        )

        client = RealKRSClient()
        is_valid, message = client.validate_krs(krs)  # No expected name

        assert is_valid
        assert message == ""

    @responses.activate
    def test_krs_not_found(self):
        """Test KRS number not found."""
        krs = "9999999999"

        responses.add(
            responses.GET,
            f"https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/{krs}?rejestr=S&format=json",
            status=404,
        )

        client = RealKRSClient()
        is_valid, message = client.validate_krs(krs)

        assert not is_valid
        assert "nie zostało znalezione w rejestrze" in message

    @responses.activate
    def test_krs_incomplete_data(self):
        """Test KRS with incomplete organization data."""
        krs = "1234567890"

        # Mock response with missing organization name
        mock_response = {
            "odpis": {
                "dane": {
                    "dzial1": {
                        "danePodmiotu": {}  # Missing nazwa
                    }
                }
            }
        }

        responses.add(
            responses.GET,
            f"https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/{krs}?rejestr=S&format=json",
            json=mock_response,
            status=200,
        )

        client = RealKRSClient()
        is_valid, message = client.validate_krs(krs)

        assert not is_valid
        assert "dane organizacji są niekompletne" in message

    @responses.activate
    def test_krs_maintenance_mode(self):
        """Test KRS API in maintenance mode."""
        krs = "1234567890"

        responses.add(
            responses.GET,
            f"https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/{krs}?rejestr=S&format=json",
            body="Przerwa techniczna",
            status=200,
        )

        client = RealKRSClient()
        is_valid, message = client.validate_krs(krs)

        # During maintenance, validation should pass with warning
        assert is_valid
        assert "⚠️" in message
        assert "Przerwa techniczna" in message

    @responses.activate
    def test_krs_network_error(self):
        """Test network error during KRS validation."""
        krs = "1234567890"

        responses.add(
            responses.GET,
            f"https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/{krs}?rejestr=S&format=json",
            body=requests.exceptions.ConnectionError(),
        )

        client = RealKRSClient()
        is_valid, message = client.validate_krs(krs)

        assert not is_valid
        assert "nie zostało znalezione w rejestrze" in message


class TestKRSIntegrationWithSchema:
    """Test KRS validation integrated with schema validation."""

    def test_schema_validation_with_valid_krs(self, mock_krs_client):
        """Test schema validation with valid KRS response."""
        mock_krs_client.set_response("1234567890", True, "")
        validator = OrganizationSchemaValidator("adres", mock_krs_client)

        data = {
            "nazwa": "Test Foundation",
            "adres": "test",
            "strona": "https://test.org",
            "krs": "1234567890",
            "dostawa": {
                "ulica": "test",
                "kod": "12-345",
                "miasto": "test",
                "telefon": "123456789",
            },
            "produkty": [{"nazwa": "test", "link": "https://test.com"}],
        }

        is_valid, errors = validator.validate_structure(data)

        assert is_valid
        assert len(errors) == 0

    def test_schema_validation_with_invalid_krs(self, mock_krs_client):
        """Test schema validation with invalid KRS response."""
        mock_krs_client.set_response("1234567890", False, "KRS not found")
        validator = OrganizationSchemaValidator("adres", mock_krs_client)

        data = {
            "nazwa": "Test Foundation",
            "adres": "test",
            "strona": "https://test.org",
            "krs": "1234567890",
            "dostawa": {
                "ulica": "test",
                "kod": "12-345",
                "miasto": "test",
                "telefon": "123456789",
            },
            "produkty": [{"nazwa": "test", "link": "https://test.com"}],
        }

        is_valid, errors = validator.validate_structure(data)

        assert not is_valid
        assert any("Walidacja KRS nie powiodła się" in error for error in errors)
        assert any("KRS not found" in error for error in errors)

    def test_schema_validation_with_krs_warning(self, mock_krs_client, capsys):
        """Test schema validation with KRS warning (maintenance mode)."""
        mock_krs_client.set_response("1234567890", True, "⚠️ Maintenance mode")
        validator = OrganizationSchemaValidator("adres", mock_krs_client)

        data = {
            "nazwa": "Test Foundation",
            "adres": "test",
            "strona": "https://test.org",
            "krs": "1234567890",
            "dostawa": {
                "ulica": "test",
                "kod": "12-345",
                "miasto": "test",
                "telefon": "123456789",
            },
            "produkty": [{"nazwa": "test", "link": "https://test.com"}],
        }

        is_valid, errors = validator.validate_structure(data)

        assert is_valid  # Should pass despite warning
        assert len(errors) == 0

        # Check that warning was printed
        captured = capsys.readouterr()
        assert "⚠️" in captured.out
        assert "Maintenance mode" in captured.out
