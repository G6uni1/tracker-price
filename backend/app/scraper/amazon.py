import re
import random
import logging
from .base import BaseScraper
from playwright.async_api import BrowserContext

logger = logging.getLogger(__name__)


class AmazonScraper(BaseScraper):
    async def extract(self, context: BrowserContext, url: str) -> dict | None:
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
            await page.wait_for_timeout(random.randint(1500, 3000))

            name = "Nome não encontrado"
            name_el = await page.query_selector("#productTitle")
            if name_el:
                name = (await name_el.inner_text()).strip()

            price = None
            price_selectors = [
                ".a-price .a-offscreen",
                "#priceblock_dealprice",
                "#priceblock_ourprice",
                "span.a-price span.a-offscreen",
            ]
            for sel in price_selectors:
                el = await page.query_selector(sel)
                if el:
                    text = await el.text_content()
                    if text:
                        cleaned = re.sub(r"[^\d,]", "", text).replace(".", "").replace(",", ".")
                        try:
                            price = float(cleaned)
                            break
                        except ValueError:
                            continue

            available = True
            body_text = await page.inner_text("body")
            if any(s in body_text.lower() for s in ["indisponível", "esgotado", "out of stock"]):
                available = False

            return {"name": name, "price": price, "availability": available, "currency": "BRL"}

        except Exception as e:
            logger.error(f"Erro Amazon {url}: {e}", exc_info=True)
            return None
        finally:
            await page.close()