"""Tests for the PubMed paper fetcher."""

from datetime import date
from unittest.mock import Mock, patch

import pytest

from pubmed_fetcher.models import Author, Paper
from pubmed_fetcher.parser import PubMedParser


def test_author_non_academic_detection():
    """Test detection of non-academic authors."""
    # Academic affiliations
    academic_author = Author(
        name="John Doe",
        affiliation="University of Science, Department of Biology"
    )
    assert not academic_author.is_non_academic
    assert academic_author.company is None

    # Company affiliations
    company_author = Author(
        name="Jane Smith",
        affiliation="Pfizer Inc., Research Division"
    )
    assert company_author.is_non_academic
    assert company_author.company == "Pfizer Inc"

    # Mixed case
    mixed_author = Author(
        name="Bob Wilson",
        affiliation="Novartis Institutes for BioMedical Research, Harvard Medical School"
    )
    assert mixed_author.is_non_academic
    assert mixed_author.company == "Novartis Institutes for BioMedical Research"


def test_paper_properties():
    """Test Paper class properties."""
    authors = [
        Author("John Doe", "University of Science", None, True, False, None),
        Author("Jane Smith", "Pfizer Inc.", "jane@pfizer.com", False, True, "Pfizer Inc"),
        Author("Bob Wilson", "Novartis", None, False, True, "Novartis")
    ]
    
    paper = Paper(
        pubmed_id="12345",
        title="Test Paper",
        publication_date=date(2023, 1, 1),
        authors=authors
    )
    
    # Test non-academic authors
    non_academic = paper.non_academic_authors
    assert len(non_academic) == 2
    assert "Jane Smith" in [a.name for a in non_academic]
    assert "Bob Wilson" in [a.name for a in non_academic]
    
    # Test company affiliations
    companies = paper.company_affiliations
    assert len(companies) == 2
    assert "Pfizer Inc" in companies
    assert "Novartis" in companies
    
    # Test corresponding author email
    assert paper.corresponding_author_email == "jane@pfizer.com"


@patch('pubmed_fetcher.api.requests.get')
def test_pubmed_api_search(mock_get):
    """Test PubMed API search functionality."""
    from pubmed_fetcher.api import PubMedAPI
    
    # Mock successful response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "esearchresult": {
            "idlist": ["12345", "67890"]
        }
    }
    mock_get.return_value = mock_response
    
    api = PubMedAPI()
    results = api.search("test query")
    
    assert len(results) == 2
    assert "12345" in results
    assert "67890" in results


def test_date_parsing():
    """Test date parsing from PubMed response."""
    parser = PubMedParser()
    
    # Test complete date
    complete_date = parser.parse_date({
        "year": "2023",
        "month": "06",
        "day": "15"
    })
    assert complete_date == date(2023, 6, 15)
    
    # Test partial date
    partial_date = parser.parse_date({
        "year": "2023"
    })
    assert partial_date == date(2023, 1, 1)
    
    # Test invalid date
    invalid_date = parser.parse_date({})
    assert invalid_date == date(1900, 1, 1)