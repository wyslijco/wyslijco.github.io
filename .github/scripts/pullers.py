from typing import Any, Self

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
    def _org_data1(self) -> dict[str, Any]:
        return self.data.get("odpis", {}).get("dane", {}).get("dzial1", {})

    @property
    def name(self) -> str:
        return self._org_data1.get("danePodmiotu", {}).get("nazwa")

    @property
    def registered_on(self) -> str:
        return (
            self.data.get("odpis", {})
            .get("naglowekA", {})
            .get("dataRejestracjiWKRS", "")
        )

    @property
    def is_opp(self) -> bool:
        return self._org_data1.get("danePodmiotu", {}).get("czyPosiadaStatusOPP", False)

    @property
    def _address_data(self) -> dict[str, Any]:
        return self._org_data1.get("siedzibaIAdres", {}).get("adres", {})

    @property
    def street(self) -> str:
        return self._address_data.get("ulica", "")

    @property
    def street_number(self) -> str:
        return self._address_data.get("nrDomu", "")

    @property
    def postal_code(self) -> str:
        return self._address_data.get("kodPocztowy", "")

    @property
    def city(self) -> str:
        return self._address_data.get("miejscowosc", "")

    @property
    def address(self) -> str:
        return f"{self.street} {self.street_number}\n{self.postal_code} {self.city}"

    @classmethod
    def get_org_by_krs(cls, issue: Issue, krs: str) -> Self | None:
        # Downloading official org data
        try:
            org = cls(krs)
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

        issue.create_comment(
            f"""Aktualne dane z KRS:
            
            **Nazwa**: {org.name}

            **Data rejestracji w KRS**: {org.registered_on}
            **Ma status OPP**: {"Tak" if org.is_opp else "Nie"}
            
            ## Adres
            {org.address}
            """
        )

        return org
