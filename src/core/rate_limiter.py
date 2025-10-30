import asyncio
import logging
import random
import time

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for controlling request frequency in web scraping."""

    def __init__(
        self, min_delay: float = 2.0, max_delay: float = 5.0, max_concurrent: int = 3
    ):
        """Initialize rate limiter with delay and concurrency limits."""
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.last_request_time = 0.0
        self.request_count = 0
        self.total_wait_time = 0.0

    async def acquire(self):
        """Acquire permission to make a request with rate limiting."""
        async with self.semaphore:
            now = time.time()
            time_since_last = now - self.last_request_time
            required_delay = random.uniform(self.min_delay, self.max_delay)

            # Wait if not enough time has passed since last request
            if time_since_last < required_delay:
                wait_time = required_delay - time_since_last
                logger.debug(f"Rate limiting: waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
                self.total_wait_time += wait_time

            self.last_request_time = time.time()
            self.request_count += 1

    def get_stats(self) -> dict:
        """Return rate limiting statistics."""
        return {
            "request_count": self.request_count,
            "total_wait_time": self.total_wait_time,
            "avg_wait_time": self.total_wait_time / max(self.request_count, 1),
        }
