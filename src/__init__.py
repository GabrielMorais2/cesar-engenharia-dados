"""Pacote da pipeline de universidades."""

from .extract import UniversityExtractor
from .load import UniversityLoader

__all__ = ["UniversityExtractor", "UniversityLoader"]
