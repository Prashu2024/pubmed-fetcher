"""Command-line interface for PubMed paper fetcher."""

import argparse
import logging
import os
import sys
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

from . import PubMedFetcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
logger = logging.getLogger("pubmed_fetcher")
console = Console()


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Fetch research papers from PubMed with pharmaceutical/biotech company affiliations."
    )

    parser.add_argument(
        "query", help="PubMed search query (supports full PubMed query syntax)"
    )

    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug logging"
    )

    parser.add_argument(
        "-f",
        "--file",
        help="Filename to save results (CSV format). If not provided, prints to console.",
    )

    parser.add_argument(
        "-m",
        "--max-results",
        type=int,
        default=100,
        help="Maximum number of results to fetch (default: 100)",
    )

    parser.add_argument(
        "-k",
        "--api-key",
        help="NCBI API key for higher rate limits",
        default=os.environ.get("NCBI_API_KEY"),
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point for the command-line interface."""
    try:
        args = parse_args()

        # Configure logging level
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Debug mode enabled")

        # Initialize fetcher
        fetcher = PubMedFetcher(api_key=args.api_key, debug=args.debug)

        # Fetch and save papers in one step
        fetcher.fetch_and_save(
            query=args.query, max_results=args.max_results, output_file=args.file
        )

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
