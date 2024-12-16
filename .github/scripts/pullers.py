import re
from typing import Optional

import requests
from github import Issue

from utils import has_label
from label import Label


class OrgDataPuller:

    def __init__(self, krs: str):
        self.krs = krs
        self.data = self.pull_data()

    def pull_data(self) -> dict | None:
        response = requests.get(f"https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/{self.krs}?rejestr=S&format=json")
        if response.status_code == 200:
            return response.json()
        else:
            raise requests.HTTPError(f"Failed to fetch data for KRS {self.krs}")

    @property
    def name(self):
        return self.data.get("odpis", {}).get("dane", {}).get("dzial1", {}).get("danePodmiotu", {}).get("nazwa")

    @staticmethod
    def validate_krs(krs):
        """
        Validates a KRS number (10-digit Polish National Court Register number).

        :param krs: str, the KRS number to validate.
        :return: bool, True if the KRS number is valid, False otherwise.
        """
        return bool(re.fullmatch(r"\d{10}", krs))

    @staticmethod
    def get_org_by_krs(issue: Issue, krs: str) -> Optional["OrgDataPuller"]:
        if not OrgDataPuller.validate_krs(krs):
            issue.create_comment("Wprowadzony numer KRS jest nieprawidłowy. Prosimy poprawić informacje.")
            issue.add_to_labels(Label.INVALID_KRS)
            return

        # Downloading official org data
        try:
            org = OrgDataPuller(krs)
        except requests.HTTPError as e:
            issue.create_comment(f"Nie udało się pobrać danych o organizacji z KRS. "
                                 f"Proszę sprawdzić, czy podany numer jest poprawny")
            issue.add_to_labels(Label.INVALID_KRS)
            return

        if has_label(issue, Label.INVALID_KRS):
            issue.remove_from_labels(Label.INVALID_KRS)

        return org
