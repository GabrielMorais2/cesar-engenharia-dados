from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from db_init import Country, University, UniversityDomain, UniversityWebPage, engine


class UniversityLoader:
    """Responsavel por transformar listas de dicionarios em dados persistidos no banco."""

    def __init__(self, db_engine=engine) -> None:
        self.db_engine = db_engine

    def load(self, universities: list[dict]) -> int:
        """Persiste universidades no banco e retorna a quantidade inserida."""
        inserted = 0

        with Session(self.db_engine) as session:
            for uni in universities:
                country_name = uni.get("country")
                country_iso2 = uni.get("alpha_two_code")

                country = session.scalar(
                    select(Country).where(Country.iso2 == country_iso2)
                )

                if country is None:
                    country = Country(
                        iso2=country_iso2,
                        name=country_name,
                    )
                    session.add(country)
                    session.flush()

                existing = session.scalar(
                    select(University).where(
                        University.country_id == country.id,
                        University.name == uni.get("name"),
                        University.state_province == uni.get("state-province"),
                        )
                )
                if existing:
                    continue

                university = University(
                    country_id=country.id,
                    name=uni.get("name"),
                    state_province=uni.get("state-province"),
                )
                session.add(university)
                session.flush()

                for domain in uni.get("domains", []):
                    session.add(
                        UniversityDomain(
                            university_id=university.id,
                            domain=domain,
                        )
                    )

                for web_page in uni.get("web_pages", []):
                    session.add(
                        UniversityWebPage(
                            university_id=university.id,
                            url=web_page,
                        )
                    )

                inserted += 1

            session.commit()

        return inserted