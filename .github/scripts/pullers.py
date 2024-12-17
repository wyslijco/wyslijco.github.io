import re
from typing import Optional

import requests
from github import Issue

from utils import has_label
from labels import Label


class KRSDataPuller:

    def __init__(self, krs: str):
        self.krs = krs
        self.data = self.pull_data()

    def pull_data(self) -> dict | None:
        response = requests.get(
            f"https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/{self.krs}?rejestr=S&format=json"
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise requests.HTTPError(f"Failed to fetch data for KRS {self.krs}")

    @property
    def name(self):
        return (
            self.data.get("odpis", {})
            .get("dane", {})
            .get("dzial1", {})
            .get("danePodmiotu", {})
            .get("nazwa")
        )

    @staticmethod
    def get_org_by_krs(issue: Issue, krs: str) -> Optional["KRSDataPuller"]:

        # Downloading official org data
        try:
            org = KRSDataPuller(krs)
        except requests.HTTPError as e:
            issue.create_comment(
                f"Nie udało się pobrać danych o organizacji z KRS. "
                f"Proszę sprawdzić, czy podany numer jest poprawny"
            )
            issue.add_to_labels(Label.INVALID_KRS)
            return

        if has_label(issue, Label.INVALID_KRS):
            issue.remove_from_labels(Label.INVALID_KRS)

        return org
