from __future__ import annotations

from typing import Iterable

import requests


class UniversityExtractor:
    """Responsavel por extrair e desserializar dados da API de universidades."""

    def __init__(
        self,
        base_url: str = "http://universities.hipolabs.com/search",
        timeout: int = 30,
    ) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def fetch_by_country(self, country: str) -> list[dict]:
        """Busca universidades de um unico pais."""
        response = requests.get(
            self.base_url,
            params={"country": country},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def fetch_by_countries(self, countries: Iterable[str]) -> list[dict]:
        """Busca universidades de varios paises e devolve uma lista unica de dicionarios."""
        result: list[dict] = []
        for country in countries:
            result.extend(self.fetch_by_country(country))
        return result
