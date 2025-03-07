"""Data models for PubMed paper fetcher."""

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from .utils import ACADEMIC_KEYWORDS, COMPANY_KEYWORDS


@dataclass
class Author:
    """Author of a paper."""

    name: str
    affiliation: Optional[str] = None
    email: Optional[str] = None
    is_corresponding: bool = False
    is_non_academic: bool = False
    company_name: Optional[str] = None

    def __post_init__(self):
        """Process affiliation after initialization."""
        if self.affiliation:
            self.is_non_academic = self._check_non_academic_affiliation()
            if self.is_non_academic:
                self.company_name = self._extract_company_name()

    def _check_non_academic_affiliation(self) -> bool:
        """Check if the affiliation is non-academic."""
        if not self.affiliation:
            return False

        affiliation_lower = self.affiliation.lower()

        # Check for academic keywords
        has_academic = any(keyword in affiliation_lower for keyword in ACADEMIC_KEYWORDS)

        # Check for company keywords
        has_company = any(
            keyword in affiliation_lower.replace(".", "").split() 
            or f" {keyword} " in f" {affiliation_lower} "
            for keyword in COMPANY_KEYWORDS
        )

        # If we have both academic and company keywords, compare their positions
        if has_academic and has_company:
            # Find the earliest position of academic and company keywords
            academic_pos = float('inf')
            company_pos = float('inf')
            
            for keyword in ACADEMIC_KEYWORDS:
                pos = affiliation_lower.find(keyword)
                if pos != -1:
                    academic_pos = min(academic_pos, pos)
            
            for keyword in COMPANY_KEYWORDS:
                pos = affiliation_lower.find(keyword)
                if pos != -1:
                    company_pos = min(company_pos, pos)
            
            # If company keyword appears before academic keyword, consider it non-academic
            return company_pos < academic_pos
        
        return has_company

    def _extract_company_name(self) -> Optional[str]:
        """Extract company name from affiliation."""
        if not self.affiliation or not self.is_non_academic:
            return None

        # Split affiliation into parts
        parts = [p.strip() for p in self.affiliation.split(",")]
        
        # Clean up parts
        parts = [p for p in parts if p and not any(skip in p.lower() for skip in [
            "department", "division", "unit", "group", "team", "laboratory",
            "research", "development", "r&d", "@", "email", "address", "tel", "fax"
        ])]

        if not parts:
            return None

        # Try to find the part that looks most like a company name
        # First try to find a part that contains a company keyword
        for part in parts:
            part_lower = part.lower()
            if any(keyword in part_lower.replace(".", "").split() for keyword in COMPANY_KEYWORDS):
                # Clean up the company name
                company_name = part.strip("., ")
                # Remove email if present
                if "@" in company_name:
                    company_name = " ".join(word for word in company_name.split() if "@" not in word)
                return company_name

        # If no company keyword found, return the first non-empty part
        company_name = parts[0].strip("., ")
        # Remove email if present
        if "@" in company_name:
            company_name = " ".join(word for word in company_name.split() if "@" not in word)
        return company_name


@dataclass
class Paper:
    """Represents a research paper from PubMed."""

    pubmed_id: str
    title: str
    publication_date: date
    authors: List[Author]
    abstract: Optional[str] = None

    @property
    def non_academic_authors(self) -> List[Author]:
        """Get list of authors from non-academic institutions."""
        return [author for author in self.authors if author.is_non_academic]

    @property
    def company_affiliations(self) -> List[str]:
        """Get unique list of company affiliations."""
        companies = {
            author.company_name
            for author in self.non_academic_authors
            if author.company_name is not None
        }
        return sorted(list(companies))

    @property
    def corresponding_author_email(self) -> Optional[str]:
        """Get email of the corresponding author if available."""
        # First try to find a corresponding author with email
        for author in self.authors:
            if author.is_corresponding and author.email:
                return author.email
        
        # If no corresponding author has email, return first author with email
        for author in self.authors:
            if author.email:
                return author.email
                
        return None
