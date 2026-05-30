import random
import re
import logging
from .base import BaseScraper
from playwright.async_api import BrowserContext

logger = logging.getLogger(__name__)


logger = logging.getLogger(__name__)


class MercadoLivreScraper(BaseScraper):
    async def extract(self, context: BrowserContext, url: str) -> dict | None:
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=60_000)
            await page.wait_for_timeout(random.randint(1000, 2000))

            # Cookie banner
            try:
                btn = page.locator("button:has-text('Entendi')")
                if await btn.is_visible(timeout=3000):
                    await btn.click()
            except Exception:
                pass

            # Nome do produto
            name = "Nome não encontrado"
            try:
                title = page.locator("h1.ui-pdp-title")
                if await title.count() > 0:
                    name = (await title.first.inner_text()).strip()
            except Exception:
                pass

            # Preço
            price = None
            price_selectors = [
                ".andes-money-amount__fraction",
                "meta[itemprop='price']",
            ]
            for sel in price_selectors:
                try:
                    if sel.startswith("meta"):
                        el = await page.query_selector(sel)
                        if el:
                            content = await el.get_attribute("content")
                            if content:
                                price = float(content)
                                break
                    else:
                        el = page.locator(sel).first
                        if await el.count() > 0:
                            text = await el.inner_text()
                            text = re.sub(r"[^\d,]", "", text).replace(".", "").replace(",", ".")
                            if text:
                                price = float(text)
                                break
                except Exception:
                    continue

            # Disponibilidade
            available = True
            page_text = await page.inner_text("body")
            out_of_stock = ["estoque esgotado", "produto indisponível", "sem estoque"]
            if any(ind in page_text.lower() for ind in out_of_stock):
                available = False

            return {
                "name": name,
                "price": price,
                "availability": available,
                "currency": "BRL",
            }

        except Exception as e:
            logger.error(f"Erro MercadoLivre {url}: {e}", exc_info=True)
            return None
        finally:
            await page.close()