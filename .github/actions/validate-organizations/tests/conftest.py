"""
Pytest configuration and shared fixtures for organization validation tests.
"""

import pytest
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Import the modules we're testing
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from repository import OrganizationRepository


class MockRepository(OrganizationRepository):
    """Mock repository for testing."""

    def __init__(self):
        self.organizations_data = {}  # slug -> filename mapping
        self.file_data = {}  # filename -> yaml content mapping
        self.load_errors = []

    def set_organizations(self, organizations: Dict[str, str]):
        """Set mock organization data (slug -> filename)."""
        self.organizations_data = organizations

    def set_file_data(self, filename: str, data: dict):
        """Set mock file content."""
        self.file_data[filename] = data

    def set_load_errors(self, errors: List[str]):
        """Set mock loading errors."""
        self.load_errors = errors

    def load_all_organizations(
        self, slug_field: str
    ) -> Tuple[Dict[str, str], List[str]]:
        """Return mock organization data with errors."""
        return self.organizations_data, self.load_errors

    def load_organization_data(self, file_path: str) -> Optional[dict]:
        """Return mock file data."""
        # Extract filename from path for lookup
        filename = Path(file_path).name
        return self.file_data.get(filename)


class MockKRSClient:
    """Mock KRS client for testing."""

    def __init__(self):
        self.responses = {}  # krs -> (is_valid, message) mapping
        self.default_response = (True, "")

    def set_response(self, krs: str, is_valid: bool, message: str = ""):
        """Set mock response for specific KRS number."""
        self.responses[krs] = (is_valid, message)

    def set_default_response(self, is_valid: bool, message: str = ""):
        """Set default response for unknown KRS numbers."""
        self.default_response = (is_valid, message)

    def validate_krs(
        self, krs: str, expected_name: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Return mock KRS validation response."""
        return self.responses.get(krs, self.default_response)


@pytest.fixture
def mock_repository():
    """Provide a mock repository for tests."""
    return MockRepository()


@pytest.fixture
def mock_krs_client():
    """Provide a mock KRS client for tests."""
    return MockKRSClient()


@pytest.fixture
def valid_organization_data():
    """Provide valid organization data for testing."""
    return {
        "nazwa": "Test Foundation",
        "adres": "test-foundation",
        "strona": "https://test-foundation.org",
        "krs": "1234567890",
        "dostawa": {
            "ulica": "Test Street 123",
            "kod": "12-345",
            "miasto": "Test City",
            "telefon": "123456789",
        },
        "produkty": [
            {"nazwa": "Test Product 1", "link": "https://example.com/product1"},
            {
                "nazwa": "Test Product 2",
                "link": "https://example.com/product2",
                "opis": "Test product description",
            },
        ],
    }


@pytest.fixture
def invalid_organization_data():
    """Provide invalid organization data for testing."""
    return {
        "nazwa": "",  # Empty name
        "adres": "INVALID-SLUG!",  # Invalid slug format
        "strona": "https://test.org",
        "krs": "123",  # Invalid KRS format
        "dostawa": {},  # Empty delivery
        "produkty": [
            {
                "nazwa": "Product 1"
                # Missing link
            }
        ],
    }


@pytest.fixture
def organization_missing_fields():
    """Provide organization data with missing required fields."""
    return {
        "nazwa": "Incomplete Foundation"
        # Missing all other required fields
    }
