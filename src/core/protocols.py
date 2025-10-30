from typing import Protocol

from .schemas import JobDetailsSchema, JobListingSchema


class ExtractorInterface(Protocol):
    """Interface for extracting job data from HTML content."""

    def extract_job_listings(self, html: str) -> list[JobListingSchema]:
        """Extract job listings from HTML."""
        ...

    def extract_job_details(self, html: str) -> JobDetailsSchema:
        """Extract detailed job information from HTML."""
        ...


class RepositoryInterface(Protocol):
    """Interface for job data repository operations."""

    def insert_listing_with_details(
        self, listing_schema: JobListingSchema, details_schema: JobDetailsSchema
    ):
        """Insert job listing with its detailed information."""
        ...

    def close(self):
        """Close repository connection."""
        ...


class ScraperInterface(Protocol):
    """Interface for job scraping operations."""

    def __init__(self, repository: RepositoryInterface) -> None:
        """Initialize scraper with repository."""
        ...

    async def scrape(self, filter: str = "", by_category: bool = False) -> None:
        """Scrape job data with optional filtering."""
        ...
