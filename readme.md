# PubMed Paper Fetcher

A Python tool to fetch research papers from PubMed and identify those with authors affiliated with pharmaceutical or biotech companies.

## Features

- Search PubMed using its full query syntax
- Identify papers with authors from pharmaceutical/biotech companies
- Export results to CSV or print to console
- Support for NCBI API key for higher rate limits
- Robust error handling and logging
- Type hints throughout the codebase
- Modular and extensible design

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Prashu2024/pubmed-fetcher.git
cd pubmed-fetcher
```

2. Install Poetry if you haven't already:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install the package and its dependencies:
```bash
poetry install
```

## Usage

The tool provides a command-line interface through the `get-papers-list` command. After installation, you can use it directly through Poetry:

```bash
# Basic usage (prints to console)
poetry run get-papers-list "cancer immunotherapy"

# Enable debug logging
poetry run get-papers-list "cancer immunotherapy" -d

# Save results to a file
poetry run get-papers-list "cancer immunotherapy" -f results.csv
```

### Command Line Options

- `query`: PubMed search query (required, supports full PubMed query syntax)
- `-h, --help`: Show help message and exit
- `-d, --debug`: Enable debug logging
- `-f FILE, --file FILE`: Save results to specified CSV file (optional)

### Output Format

The program outputs a CSV with the following columns:
- PubmedID: Unique identifier for the paper
- Title: Title of the paper
- Publication Date: Date the paper was published
- Non-academic Author(s): Names of authors affiliated with non-academic institutions
- Company Affiliation(s): Names of pharmaceutical/biotech companies
- Corresponding Author Email: Email address of the corresponding author

## Code Organization

The project follows a modular structure:

```
pubmed_fetcher/
├── src/
│   └── pubmed_fetcher/
│       ├── __init__.py      # Package initialization
│       ├── api.py           # PubMed API interaction
│       ├── cli.py           # Command-line interface
│       ├── models.py        # Data models (Author, Paper)
│       ├── parser.py        # Response parsing
│       └── utils.py         # Keywords and utilities
├── tests/                   # Unit tests
├── pyproject.toml          # Project configuration
└── README.md               # Documentation
```

## Development

### Setting up the Development Environment

1. Clone the repository and install dependencies:
```bash
git clone https://github.com/yourusername/pubmed-fetcher.git
cd pubmed-fetcher
poetry install
```

2. Run tests:
```bash
poetry run pytest
```

### Type Checking

The project uses MyPy for static type checking:

```bash
poetry run mypy src/pubmed_fetcher
```

### Code Formatting

The project uses Black and isort for code formatting:

```bash
poetry run black src/pubmed_fetcher tests
poetry run isort src/pubmed_fetcher tests
```

## Tools Used

- [Poetry](https://python-poetry.org/): Dependency management and packaging
- [Requests](https://requests.readthedocs.io/): HTTP library for API calls
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/): XML parsing
- [Rich](https://rich.readthedocs.io/): Terminal formatting and logging
- [MyPy](https://mypy.readthedocs.io/): Static type checking
- [Black](https://black.readthedocs.io/): Code formatting
- [isort](https://pycqa.github.io/isort/): Import sorting
- [Pytest](https://docs.pytest.org/): Testing framework

