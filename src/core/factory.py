from src.seek.scraper import SeekScraper

from .enums import JobSite
from .protocols import RepositoryInterface


class JobScraperFactory:
    @staticmethod
    def get_scraper(job_site: JobSite, repository: RepositoryInterface):
        """Returns the appropriate scraper instance for the given job site."""
        if job_site == JobSite.SEEK:
            return SeekScraper(repository)
        raise ValueError(f"Unsupported job site: {job_site}")
