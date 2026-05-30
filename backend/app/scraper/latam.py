import re
import random
import logging
from .base import BaseScraper
from playwright.async_api import BrowserContext

logger = logging.getLogger(__name__)


class LatamScraper(BaseScraper):
    async def extract(self, context: BrowserContext, url: str) -> dict | None:
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=90_000)
            await page.wait_for_timeout(random.randint(3000, 6000))

            title = await page.title()
            name = title.strip() if title else "Voo"

            price = None
            price_elements = page.locator("[class*='price'], [class*='amount'], .fare-amount")
            count = await price_elements.count()
            if count > 0:
                texts = await price_elements.all_inner_texts()
                numeric_prices = []
                for t in texts:
                    for n in re.findall(r"[\d.,]+", t):
                        try:
                            val = float(n.replace(".", "").replace(",", "."))
                            if val > 50:  # preços reais de passagem
                                numeric_prices.append(val)
                        except ValueError:
                            continue
                if numeric_prices:
                    price = min(numeric_prices)

            if not price:
                meta = await page.query_selector("meta[itemprop='price']")
                if meta:
                    content = await meta.get_attribute("content")
                    if content:
                        try:
                            price = float(content)
                        except ValueError:
                            pass

            return {
                "name": name,
                "price": price,
                "availability": price is not None,
                "currency": "BRL",
            }

        except Exception as e:
            logger.error(f"Erro Latam {url}: {e}", exc_info=True)
            return None
        finally:
            await page.close()