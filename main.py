from src.extract import UniversityExtractor
from src.load import UniversityLoader


def main() -> None:
    countries = ["Brazil", "Argentina", "Chile"]

    extractor = UniversityExtractor()
    loader = UniversityLoader()

    universities = extractor.fetch_by_countries(countries)
    inserted = loader.load(universities)

    print(f"Universidades inseridas: {inserted}")


if __name__ == "__main__":
    main()