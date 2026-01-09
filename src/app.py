"""Job scraper application entry point."""

import argparse
import asyncio
import logging

from src.core.enums import JobSite
from src.core.factory import JobScraperFactory
from src.core.repositories import get_repository


def setup_logging():
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def create_parser():
    """Create and configure CLI argument parser."""
    parser = argparse.ArgumentParser(description="Run job scraper for a specific site.")

    parser.add_argument(
        "--site",
        type=str,
        choices=[site.value for site in JobSite],
        help="The job site to scrape (e.g., seek).",
    )

    parser.add_argument(
        "--list-sites",
        action="store_true",
        help="List all available job sites and exit.",
    )

    parser.add_argument(
        "--by-category",
        action="store_true",
        default=False,
        help="Scrape jobs by category. Use --by-category to scrape by category instead of by filter (default).",
    )

    parser.add_argument(
        "--min-delay",
        type=float,
        help="Minimum delay between requests in seconds (overrides config).",
    )

    parser.add_argument(
        "--max-delay",
        type=float,
        help="Maximum delay between requests in seconds (overrides config).",
    )

    parser.add_argument(
        "--max-concurrent",
        type=int,
        help="Maximum concurrent requests (overrides config).",
    )

    return parser


async def run_scraper(
    site_name: str, by_category: bool, rate_limit_overrides: dict | None = None
):
    """Run the job scraper with given parameters."""
    site = JobSite(site_name)
    logging.info(f"Starting job scraper for site: {site.value}")

    # Create repository
    repository = get_repository()

    # Create scraper using factory
    scraper = JobScraperFactory.get_scraper(site, repository)

    # Apply rate limiting overrides if provided
    if rate_limit_overrides and hasattr(scraper, "rate_limiter"):
        if rate_limit_overrides.get("min_delay") is not None:
            scraper.rate_limiter.min_delay = rate_limit_overrides["min_delay"]
        if rate_limit_overrides.get("max_delay") is not None:
            scraper.rate_limiter.max_delay = rate_limit_overrides["max_delay"]
        if rate_limit_overrides.get("max_concurrent") is not None:
            # Replace existing semaphore with new limit
            scraper.rate_limiter.semaphore = asyncio.Semaphore(
                rate_limit_overrides["max_concurrent"]
            )

        logging.info(
            f"Rate limiting: {scraper.rate_limiter.min_delay}-{scraper.rate_limiter.max_delay}s delay, "
            f"max {rate_limit_overrides.get('max_concurrent', 'default')} concurrent"
        )

    # Run the scraper
    await scraper.scrape(by_category=by_category)


async def main():
    """Main application entry point."""
    setup_logging()
    parser = create_parser()
    args = parser.parse_args()

    if args.list_sites:
        print("Available job sites:")
        for site in JobSite:
            print(f"  - {site.value}")
        return

    if not args.site:
        parser.error("--site is required unless --list-sites is used.")

    # Build rate limiting overrides from CLI args
    rate_limit_overrides = {}
    if args.min_delay is not None:
        rate_limit_overrides["min_delay"] = args.min_delay
    if args.max_delay is not None:
        rate_limit_overrides["max_delay"] = args.max_delay
    if args.max_concurrent is not None:
        rate_limit_overrides["max_concurrent"] = args.max_concurrent

    await run_scraper(args.site, args.by_category, rate_limit_overrides or None)


if __name__ == "__main__":
    asyncio.run(main())
