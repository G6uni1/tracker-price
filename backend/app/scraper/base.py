import asyncio
import logging
import random
import traceback
from abc import ABC, abstractmethod
from playwright.async_api import async_playwright, BrowserContext, Browser
from playwright_stealth import stealth_async
from .utils import get_random_user_agent, random_delay, get_random_proxy

logger = logging.getLogger(__name__)

SCRAPE_TIMEOUT_SECONDS = 120  # timeout global por tentativa


class BaseScraper(ABC):
    max_retries = 2

    async def _create_context(self, browser: Browser) -> BrowserContext:
        proxy = get_random_proxy()
        context_options = {
            "viewport": {
                "width": random.randint(1280, 1920),
                "height": random.randint(720, 1080),
            },
            "user_agent": get_random_user_agent(),
            "locale": "pt-BR",
            "timezone_id": "America/Sao_Paulo",
        }
        if proxy:
            context_options["proxy"] = {"server": proxy}

        context = await browser.new_context(**context_options)
        page = await context.new_page()
        await stealth_async(page)
        await page.close()
        return context

    async def extract_with_retry(self, url: str) -> dict | None:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ],
            )
            try:
                for attempt in range(1, self.max_retries + 1):
                    context = await self._create_context(browser)
                    try:
                        # Timeout global para cada tentativa
                        result = await asyncio.wait_for(
                            self.extract(context, url),
                            timeout=SCRAPE_TIMEOUT_SECONDS,
                        )
                        return result
                    except asyncio.TimeoutError:
                        logger.warning(
                            f"Timeout ({SCRAPE_TIMEOUT_SECONDS}s) na tentativa {attempt} para {url}"
                        )
                        if attempt == self.max_retries:
                            return None
                    except Exception as e:
                        logger.warning(f"Tentativa {attempt} falhou para {url}: {e}")
                        if attempt == self.max_retries:
                            logger.error(f"Todas tentativas falharam para {url}:\n{traceback.format_exc()}")
                            return None
                        await random_delay(5, 10)
                    finally:
                        await context.close()
            finally:
                await browser.close()
        return None

    @abstractmethod
    async def extract(self, context: BrowserContext, url: str) -> dict | None:
        pass