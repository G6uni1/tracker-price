import logging
import random
import traceback
from abc import ABC, abstractmethod
from playwright.async_api import async_playwright, BrowserContext
from playwright_stealth import stealth_async
from .utils import get_random_user_agent, random_delay, get_random_proxy

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    max_retries = 2

    async def create_context(self) -> BrowserContext:
        p = await async_playwright().start()
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        proxy = get_random_proxy()
        context_options = {
            "viewport": {"width": random.randint(1280, 1920), "height": random.randint(720, 1080)},
            "user_agent": get_random_user_agent(),
        }
        if proxy:
            context_options["proxy"] = {"server": proxy}
        context = await browser.new_context(**context_options)
        # Aplica stealth na primeira página para sujar o contexto
        page = await context.new_page()
        await stealth_async(page)
        await page.close()
        return context

    async def extract_with_retry(self, url: str) -> dict | None:
        for attempt in range(1, self.max_retries + 1):
            try:
                return await self.extract(url)
            except Exception as e:
                logger.warning(f"Tentativa {attempt} falhou para {url}: {e}")
                if attempt == self.max_retries:
                    logger.error(f"Todas as tentativas falharam para {url}. Traceback: {traceback.format_exc()}")
                    return None
                await random_delay(5, 10)  # espera mais antes de retry

    @abstractmethod
    async def extract(self, url: str) -> dict:
        pass

    async def delay(self):
        await random_delay()