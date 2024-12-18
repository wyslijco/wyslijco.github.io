from typing import Optional, Self

import requests
from github import Issue
from requests import JSONDecodeError

from exceptions import KRSMaintenanceError
from labels import Label
from utils import has_label


class KRSDataPuller:
    def __init__(self, krs: str):
        self.krs = krs
        self.data = self.pull_data()

    def pull_data(self) -> dict | None:
        response = requests.get(
            f"https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/{self.krs}?rejestr=S&format=json"
        )
        if response.status_code == 200:
            try:
                return response.json()
            except JSONDecodeError:
                if "Przerwa techniczna" in response.text:
                    raise KRSMaintenanceError(
                        f"Przerwa techniczna serwisu weryfikującego KRS. "
                        f"Proszę [zweryfikować KRS ręcznie]"
                        f"(https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/{self.krs}?rejestr=S&format=json)."
                    )
                raise
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

    @classmethod
    def get_org_by_krs(cls, issue: Issue, krs: str) -> Self | None:
        # Downloading official org data
        try:
            org = KRSDataPuller(krs)
        except KRSMaintenanceError as e:
            issue.create_comment(str(e))
            issue.add_to_labels(Label.INVALID_KRS)
            return
        except requests.HTTPError:
            issue.create_comment(
                "Nie udało się pobrać danych o organizacji z KRS. "
                "Proszę sprawdzić, czy podany numer jest poprawny"
            )
            return

        if has_label(issue, Label.INVALID_KRS):
            issue.remove_from_labels(Label.INVALID_KRS)

        return org
