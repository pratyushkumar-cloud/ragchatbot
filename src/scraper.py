"""
Playwright-based web scraper for dynamic content.
"""

import logging
from typing import Dict, Optional
from playwright.async_api import async_playwright, Page, Browser

logger = logging.getLogger(__name__)


class WebScraper:
    """Reusable Playwright scraper for dynamic web content."""

    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30000,
        retries: int = 3
    ):
        """
        Initialize the web scraper.

        Args:
            headless: Run browser in headless mode
            timeout: Page load timeout in milliseconds
            retries: Number of retry attempts on failure
        """
        self.headless = headless
        self.timeout = timeout
        self.retries = retries

    async def scrape(
        self,
        url: str,
        wait_for_network_idle: bool = True
    ) -> str:
        """
        Scrape a webpage and return rendered HTML.

        Args:
            url: URL to scrape
            wait_for_network_idle: Wait for network to be idle before extracting

        Returns:
            Rendered HTML content
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()

            for attempt in range(self.retries):
                try:
                    logger.info(f"Scraping {url} (attempt {attempt + 1}/{self.retries})")

                    response = await page.goto(
                        url,
                        wait_until="domcontentloaded",
                        timeout=self.timeout
                    )

                    if wait_for_network_idle:
                        await page.wait_for_load_state("networkidle", timeout=self.timeout)

                    html = await page.content()
                    logger.info(f"Successfully scraped {url}")
                    return html

                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} failed for {url}: {e}")
                    if attempt == self.retries - 1:
                        raise
                    await page.wait_for_timeout(2000)  # Wait before retry

            await browser.close()

    async def close(self):
        """Clean up resources."""
        pass


async def scrape_webpage(
    url: str,
    headless: bool = True,
    timeout: int = 30000,
    wait_for_network_idle: bool = True
) -> str:
    """
    Convenience function to scrape a webpage.

    Args:
        url: URL to scrape
        headless: Run browser in headless mode
        timeout: Page load timeout in milliseconds
        wait_for_network_idle: Wait for network to be idle

    Returns:
        Rendered HTML content
    """
    scraper = WebScraper(headless=headless, timeout=timeout)
    return await scraper.scrape(url, wait_for_network_idle)
