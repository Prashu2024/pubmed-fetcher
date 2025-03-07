"""PubMed Paper Fetcher - A tool to identify papers with pharma/biotech company affiliations."""

from .api import PubMedAPI
from .models import Author, Paper
from .parser import PubMedParser
from .fetcher import PubMedFetcher

__version__ = "0.1.0"
__all__ = ["PubMedFetcher", "PubMedAPI", "Author", "Paper", "PubMedParser"]
