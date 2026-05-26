from abc import ABC, abstractmethod
from playwright.async_api import async_playwright, BrowserContext
from playwright_stealth import stealth_async
import random
import asyncio

class BaseScraper(ABC):
    @abstractmethod
    async def extract(self, url: str) -> dict:
        """Retorna {name, price, availability, ...}"""
        pass

    async def create_context(self) -> BrowserContext:
        p = await async_playwright().start()
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        # Aplica stealth
        page = await context.new_page()
        await stealth_async(page)
        await page.close()
        return context

    async def delay(self):
        await asyncio.sleep(random.uniform(1, 3))