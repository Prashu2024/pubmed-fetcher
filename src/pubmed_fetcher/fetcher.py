"""Main module for fetching and processing PubMed papers."""

import csv
import logging
import sys
from typing import List, Optional, TextIO

from rich.logging import RichHandler

from .api import PubMedAPI
from .models import Paper
from .parser import PubMedParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
logger = logging.getLogger("pubmed_fetcher")


class PubMedFetcher:
    """Main class for fetching and processing PubMed papers."""

    def __init__(self, api_key: Optional[str] = None, debug: bool = False):
        """Initialize the PubMed fetcher.

        Args:
            api_key: Optional NCBI API key for higher rate limits
            debug: Enable debug logging if True
        """
        self.api = PubMedAPI(api_key=api_key)
        self.parser = PubMedParser()

        if debug:
            logging.getLogger().setLevel(logging.DEBUG)

    def search_pubmed(self, query: str, max_results: int = 100) -> List[str]:
        """Search PubMed for papers matching the query.

        Args:
            query: PubMed search query
            max_results: Maximum number of results to return

        Returns:
            List of PubMed IDs
        """
        logger.info(f"Searching PubMed with query: {query}")
        return self.api.search(query, max_results)

    def process_papers(self, pmids: List[str]) -> List[Paper]:
        """Fetch and process papers from their PubMed IDs.

        Args:
            pmids: List of PubMed IDs to process

        Returns:
            List of processed Paper objects
        """
        if not pmids:
            logger.warning("No PubMed IDs provided to process")
            return []

        logger.info(f"Fetching details for {len(pmids)} papers")
        paper_details = self.api.fetch_details(pmids)
        return self.parser.parse_search_results(paper_details)

    def save_results_to_csv(
        self, papers: List[Paper], output_file: Optional[str] = None
    ) -> None:
        """Save paper results to CSV file or print to console.

        Args:
            papers: List of Paper objects to save
            output_file: Optional file path to save results to
        """
        if not papers:
            logger.warning("No papers to save")
            return

        # Prepare CSV data
        headers = [
            "PubmedID",
            "Title",
            "Publication Date",
            "Non-academic Author(s)",
            "Company Affiliation(s)",
            "Corresponding Author Email",
        ]

        rows = []
        for paper in papers:
            non_academic_authors = "; ".join(
                author.name for author in paper.non_academic_authors
            )
            company_affiliations = "; ".join(paper.company_affiliations)

            rows.append(
                [
                    paper.pubmed_id,
                    paper.title,
                    paper.publication_date.isoformat(),
                    non_academic_authors,
                    company_affiliations,
                    paper.corresponding_author_email or "",
                ]
            )

        # Write to file or stdout
        output: TextIO = (
            open(output_file, "w", newline="") if output_file else sys.stdout
        )
        try:
            writer = csv.writer(output)
            writer.writerow(headers)
            writer.writerows(rows)

            if output_file:
                logger.info(f"Results saved to {output_file}")

        finally:
            if output_file and output != sys.stdout:
                output.close()

    def fetch_and_save(
        self, query: str, max_results: int = 100, output_file: Optional[str] = None
    ) -> None:
        """Convenience method to search, process, and save results in one step.

        Args:
            query: PubMed search query
            max_results: Maximum number of results to return
            output_file: Optional file path to save results to
        """
        pmids = self.search_pubmed(query, max_results)
        papers = self.process_papers(pmids)
        self.save_results_to_csv(papers, output_file) 