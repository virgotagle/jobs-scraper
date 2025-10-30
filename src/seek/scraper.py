import logging
from typing import AsyncGenerator
from urllib.parse import urlencode, urljoin

from tenacity import retry, stop_after_attempt, wait_fixed

from src.core.config import config
from src.core.protocols import RepositoryInterface
from src.core.rate_limiter import RateLimiter
from src.core.schemas import JobDetailsSchema, JobListingSchema
from src.core.utils.browser import BrowserHelper, Page

from .extractor import SeekExtractor

logger = logging.getLogger(__name__)


class SeekScraper:
    """Scrapes job listings and details from Seek.com.au."""

    def __init__(self, repository: RepositoryInterface) -> None:
        """Initialize scraper with repository and rate limiting."""
        self.repository = repository
        self.extractor = SeekExtractor()
        self.config = config.get("sites", {}).get("seek", {})

        # Initialize rate limiter with config values
        self.rate_limiter = RateLimiter(
            min_delay=self.config.get("min_delay", 2.0),
            max_delay=self.config.get("max_delay", 4.0),
            max_concurrent=self.config.get("max_concurrent", 2),
        )

    async def scrape(self, by_category: bool = True) -> None:
        """Scrape all job listings and their details, saving to repository."""
        job_count = 0
        async with BrowserHelper() as browser:
            page: Page = await browser.new_page()
            async for job_listing in self.scrape_job_listings(page, by_category):
                job_count += 1
                logger.debug(
                    f"Processing job {job_count}: {job_listing.job_id} - {job_listing.title}"
                )
                job_details: JobDetailsSchema = await self.scrape_job_details(
                    page, job_listing.job_details_url
                )
                self.repository.insert_listing_with_details(job_listing, job_details)
                logger.debug(f"Saved job {job_listing} to database")

        # Log rate limiting statistics
        stats = self.rate_limiter.get_stats()
        logger.info(f"Scraping finished: {job_count} total jobs processed")
        logger.info(
            f"Rate limiter stats: {stats['request_count']} requests, "
            f"{stats['total_wait_time']:.1f}s total wait time, "
            f"{stats['avg_wait_time']:.1f}s avg wait time"
        )

    async def scrape_job_listings(
        self, page: Page, by_category: bool = True
    ) -> AsyncGenerator[JobListingSchema, None]:
        """Generate job listings across all pages until exhausted."""
        page_number = 1
        while True:
            job_listings = await self.scrape_job_listing(
                page,
                page_number=page_number,
                by_category=by_category,
            )
            for job_listing in job_listings:
                yield job_listing
            # Seek shows 22 jobs per page when there are more pages
            if len(job_listings) == 22:
                page_number += 1
                logger.info(
                    f"Page {page_number - 1} complete. Moving to page {page_number}"
                )
            else:
                logger.info(
                    f"Page {page_number} complete. Last page reached - stopping pagination"
                )
                break

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    async def scrape_job_listing(
        self,
        page: Page,
        page_number: int = 1,
        by_category: bool = True,
    ) -> list[JobListingSchema]:
        """Scrape job listings from a single page."""
        try:
            # Apply rate limiting before making request
            await self.rate_limiter.acquire()

            # Build URL path based on search type
            if by_category:
                path = f"{self.config['category']}/{self.config['location']}"
            else:
                path = f"{self.config['filter']}/{self.config['location']}"

            query_params = {"page": page_number} if page_number > 1 else {}
            full_url = urljoin(self.config["url"], path)
            if query_params:
                full_url += "?" + urlencode(query_params)

            logger.info(
                f"Scraping page {page_number} for {self.config['category'] if by_category else self.config['filter']} in {self.config['location']}"
            )

            await page.goto(full_url, wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle")
            job_listings = self.extractor.extract_job_listings(await page.content())
            logger.info(f"Found {len(job_listings)} jobs on page {page_number}")
            return job_listings
        except Exception as e:
            logging.error(
                f"Failed to scrape job listings for {self.config['category'] if by_category else self.config['filter']} in {self.config['location']} on page {page_number}: {e}"
            )
            raise RuntimeError(f"Failed to scrape job listings: {e}") from e

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    async def scrape_job_details(self, page: Page, url: str) -> JobDetailsSchema:
        """Scrape detailed job information from a job posting URL."""
        try:
            # Apply rate limiting before making request
            await self.rate_limiter.acquire()

            logger.debug(f"Fetching job details from: {url}")
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle")
            return self.extractor.extract_job_details(await page.content())
        except Exception as e:
            logging.error(f"Failed to scrape job details for URL {url}: {e}")
            raise RuntimeError(f"Failed to scrape job details: {e}") from e
