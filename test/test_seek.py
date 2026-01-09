import pytest

from src.core.repositories import SQLiteRepository
from src.core.utils.browser import BrowserHelper, Page
from src.seek.scraper import SeekScraper


@pytest.mark.asyncio
async def test_seek() -> None:
    repo = SQLiteRepository("sqlite:///jobs.db")
    async with BrowserHelper() as browser:
        page: Page = await browser.new_page()
        scraper = SeekScraper(repo)
        job_listings = await scraper.scrape_job_listing(
            page, page_number=1, by_category=True
        )
        job_listing = job_listings[0]
        assert job_listing.company_name is not None
        assert job_listing.location is not None
        assert job_listing.title is not None
        job_details = await scraper.scrape_job_details(
            page, job_listing.job_details_url
        )
        assert job_listing.job_id == job_details.job_id
        assert job_details.details is not None
        assert job_details.status
