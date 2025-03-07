"""Parser module for PubMed API responses."""

import logging
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from .models import Author, Paper

logger = logging.getLogger(__name__)


class PubMedParser:
    """Parser for PubMed API responses."""

    @staticmethod
    def parse_date(date_str: str) -> date:
        """Parse date string from PubMed response.

        Args:
            date_str: Date string in format YYYY-Mon-DD or YYYY-MM-DD

        Returns:
            Python date object
        """
        try:
            # Try parsing YYYY-MM-DD format first
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            try:
                # Try parsing YYYY-Mon-DD format
                return datetime.strptime(date_str, "%Y-%b-%d").date()
            except ValueError:
                logger.warning(f"Could not parse date string: {date_str}")
                return date(1900, 1, 1)  # Return default date for unparseable dates

    @staticmethod
    def parse_author(author_data: Dict[str, Any]) -> Author:
        """Parse author data from PubMed response.

        Args:
            author_data: Dictionary containing author information

        Returns:
            Author object
        """
        # Get author name
        name = author_data.get("name", "")
        if not name:
            name = "Unknown Author"

        # Get affiliation and email
        affiliation = None
        email = None

        # Check for affiliation in AffiliationInfo
        if "AffiliationInfo" in author_data:
            affiliations = []
            for aff_info in author_data["AffiliationInfo"]:
                if isinstance(aff_info, dict) and "Affiliation" in aff_info:
                    aff_text = aff_info["Affiliation"].strip()
                    if aff_text:
                        affiliations.append(aff_text)
            if affiliations:
                affiliation = "; ".join(affiliations)

        # If no AffiliationInfo, check for direct affiliation field
        if not affiliation:
            if isinstance(author_data.get("affiliation"), list):
                affiliations = [aff.strip() for aff in author_data["affiliation"] if aff and aff.strip()]
                if affiliations:
                    affiliation = "; ".join(affiliations)
            elif isinstance(author_data.get("affiliation"), str):
                affiliation = author_data["affiliation"].strip()

        # Try to extract email from affiliation if present
        if affiliation:
            # Look for email in the affiliation string
            parts = affiliation.split()
            for part in parts:
                if "@" in part and "." in part:  # Basic email validation
                    email_candidate = part.strip(".,()<>[]{}").lower()
                    if "@" in email_candidate and "." in email_candidate.split("@")[1]:
                        email = email_candidate
                        # Clean up the affiliation by removing the email
                        affiliation = affiliation.replace(part, "").strip()
                        break

        # Check if author is corresponding
        is_corresponding = bool(email) or (
            affiliation and any(term in affiliation.lower() 
                              for term in ["corresponding", "correspondence", "whom correspondence"])
        ) or author_data.get("is_corresponding", False)

        return Author(
            name=name,
            affiliation=affiliation,
            email=email,
            is_corresponding=is_corresponding,
        )

    @classmethod
    def parse_paper(cls, paper_data: Dict[str, Any]) -> Optional[Paper]:
        """Parse paper data from PubMed response.

        Args:
            paper_data: Dictionary containing paper information

        Returns:
            Paper object or None if parsing fails
        """
        try:
            # Extract basic paper information
            pubmed_id = str(paper_data.get("uid", ""))
            title = paper_data.get("title", "").strip()
            if not title or not pubmed_id:
                logger.warning(f"Missing required paper data for PMID {pubmed_id}")
                return None

            # Parse publication date
            pub_date_str = paper_data.get("pubdate", "")
            if not pub_date_str:
                pub_date = date(1900, 1, 1)
            else:
                pub_date = cls.parse_date(pub_date_str)

            # Parse authors
            authors = []
            for author_data in paper_data.get("authors", []):
                try:
                    author = cls.parse_author(author_data)
                    authors.append(author)
                except Exception as e:
                    logger.warning(f"Error parsing author data: {e}")
                    continue

            # Create paper object
            return Paper(
                pubmed_id=pubmed_id,
                title=title,
                publication_date=pub_date,
                authors=authors,
                abstract=paper_data.get("abstract", ""),
            )

        except Exception as e:
            logger.error(f"Error parsing paper data: {e}")
            return None

    @classmethod
    def parse_search_results(cls, api_response: Dict[str, Any]) -> List[Paper]:
        """Parse full search results from PubMed API.

        Args:
            api_response: Dictionary containing PubMed API response

        Returns:
            List of Paper objects
        """
        papers = []

        if "result" not in api_response:
            logger.error("No result key in API response")
            return papers

        for uid, paper_data in api_response["result"].items():
            if uid == "uids":  # Skip the uids list
                continue

            paper = cls.parse_paper(paper_data)
            if paper:
                papers.append(paper)

        return papers
