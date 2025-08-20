"""
KRS data puller for organization validation.
Adapted from the main CLI KRS validation logic.
"""

import requests
from typing import Optional


class KRSDataPuller:
    """Pulls and validates organization data from Polish KRS registry."""

    def __init__(self, krs: str):
        self.krs = krs
        self.data = self._pull_data()

    def _pull_data(self) -> Optional[dict]:
        """Pull organization data from KRS API."""
        try:
            response = requests.get(
                f"https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/{self.krs}?rejestr=S&format=json",
                timeout=10,
            )

            if response.status_code == 200:
                try:
                    return response.json()
                except requests.exceptions.JSONDecodeError:
                    if "Przerwa techniczna" in response.text:
                        raise KRSMaintenanceError(
                            f"Przerwa techniczna serwisu weryfikującego KRS. "
                            f"Proszę zweryfikować KRS ręcznie: "
                            f"https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/{self.krs}?rejestr=S&format=json"
                        )
                    raise
            else:
                raise requests.HTTPError(f"Failed to fetch data for KRS {self.krs}")

        except requests.exceptions.RequestException as e:
            raise requests.HTTPError(f"Network error fetching KRS {self.krs}: {e}")

    @property
    def name(self) -> Optional[str]:
        """Get organization name from KRS data."""
        if not self.data:
            return None

        return (
            self.data.get("odpis", {})
            .get("dane", {})
            .get("dzial1", {})
            .get("danePodmiotu", {})
            .get("nazwa")
        )

    @classmethod
    def get_organization_data(cls, krs: str) -> Optional["KRSDataPuller"]:
        """
        Get organization data from KRS registry.

        Returns:
            KRSDataPuller instance if successful, None if failed
        """
        try:
            return cls(krs)
        except (KRSMaintenanceError, requests.HTTPError):
            return None


class KRSMaintenanceError(Exception):
    """Raised when KRS API is in maintenance mode."""

    pass
