"""Browser automation helper with stealth capabilities."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)
from playwright_stealth import Stealth  # type: ignore

logger = logging.getLogger(__name__)


class BrowserHelper:
    """Async context manager for browser automation with stealth capabilities."""

    def __init__(
        self,
        headless: bool = True,
        state_storage_path: Optional[Path] = None,
        browser_args: Optional[Dict[str, Any]] = None,
        context_args: Optional[Dict[str, Any]] = None,
        stealth_config: Optional[Dict[str, Any]] = None,
        apply_stealth: bool = True,
    ):
        """Initialize browser helper with configuration options."""
        self.headless = headless
        self.state_storage_path = state_storage_path
        self.browser_args = browser_args or {}
        self.context_args = context_args or {}
        self.apply_stealth = apply_stealth
        self.stealth_config = stealth_config or {}

        # Resource tracking for proper cleanup
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.playwright: Optional[Playwright] = None
        self._stealth_manager: Any = None
        self._pages: List[Page] = []

    async def __aenter__(self) -> "BrowserHelper":
        """Initialize and return configured browser context."""
        try:
            # Initialize Playwright with or without stealth
            if self.apply_stealth:
                # Stealth wrapper applies anti-detection to all pages
                stealth = Stealth(**self.stealth_config)
                self._stealth_manager = stealth.use_async(async_playwright())
                if self._stealth_manager:
                    self.playwright = await self._stealth_manager.__aenter__()
            else:
                self._stealth_manager = async_playwright()
                self.playwright = await self._stealth_manager.__aenter__()

            if not self.playwright:
                raise RuntimeError("Failed to initialize Playwright")

            # Prepare browser launch arguments
            launch_args = {
                "headless": self.headless,
                "channel": "chrome",
                **self.browser_args,
            }

            # Add anti-detection flags for stealth mode
            if self.apply_stealth and "args" not in launch_args:
                launch_args["args"] = []
            if (
                self.apply_stealth
                and "--disable-blink-features=AutomationControlled"
                not in launch_args.get("args", [])
            ):
                launch_args["args"].append(
                    "--disable-blink-features=AutomationControlled"
                )

            # Launch browser
            self.browser = await self.playwright.chromium.launch(**launch_args)
            logger.info(
                f"Browser launched (headless={self.headless}, stealth={self.apply_stealth})"
            )

            # Prepare context arguments
            context_args = {**self.context_args}

            # Load state storage if available
            if self.state_storage_path and self.state_storage_path.exists():
                try:
                    context_args["storage_state"] = str(self.state_storage_path)
                    logger.info(f"Loaded browser state from {self.state_storage_path}")
                except Exception as e:
                    logger.warning(f"Failed to load state storage: {e}")

            # Create context with stealth already applied
            self.context = await self.browser.new_context(**context_args)

            return self

        except (OSError, RuntimeError) as e:
            await self._cleanup()
            raise RuntimeError(f"Failed to initialize browser: {e}") from e

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up all browser resources."""
        await self._cleanup()

    async def _cleanup(self):
        """Cleanup all resources with error suppression."""
        # Close all tracked pages
        for page in self._pages:
            try:
                if not page.is_closed():
                    await page.close()
            except Exception as e:
                logger.debug(f"Error closing page: {e}")
        self._pages.clear()

        # Close context
        if self.context:
            try:
                await self.context.close()
            except Exception as e:
                logger.debug(f"Error closing context: {e}")
            finally:
                self.context = None

        # Close browser
        if self.browser:
            try:
                await self.browser.close()
            except Exception as e:
                logger.debug(f"Error closing browser: {e}")
            finally:
                self.browser = None

        # Close playwright/stealth manager
        if self._stealth_manager:
            try:
                await self._stealth_manager.__aexit__(None, None, None)
            except Exception as e:
                logger.debug(f"Error closing playwright manager: {e}")
            finally:
                self._stealth_manager = None
                self.playwright = None

    async def new_page(self, **page_args) -> Page:
        """Create a new page with automatic cleanup tracking."""
        if self.context is None:
            raise ValueError("Browser context is not initialized.")

        page = await self.context.new_page(**page_args)
        self._pages.append(page)
        logger.debug(f"Created new page (total pages: {len(self._pages)})")
        return page

    async def save_state_storage(self, path: Optional[Path] = None) -> Path:
        """Save browser state (cookies, localStorage) to file."""
        if self.context is None:
            raise ValueError("Browser context is not initialized.")

        save_path = path or self.state_storage_path
        if save_path is None:
            raise ValueError("No path specified for saving state.")

        save_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            await self.context.storage_state(path=str(save_path))
            logger.info(f"Saved browser state to {save_path}")
            return save_path
        except OSError as e:
            logger.error(f"Failed to save browser state: {e}")
            raise

    @property
    def is_initialized(self) -> bool:
        """Return True if browser and context are ready."""
        return self.browser is not None and self.context is not None
