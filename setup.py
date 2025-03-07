"""
Setup script for publishing to TestPyPI.
"""
from setuptools import find_packages, setup

setup(
    name="pubmed-paper-fetcher",
    version="0.1.0",
    description="Tool to fetch PubMed papers with pharma/biotech company affiliations",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
        "lxml>=4.9.3",
        "rich>=13.5.2",
    ],
    entry_points={
        "console_scripts": [
            "get-papers-list=pubmed_paper_fetcher.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
