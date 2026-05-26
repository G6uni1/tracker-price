from .base import BaseScraper
from playwright.async_api import async_playwright, Page
import re
import logging

logger = logging.getLogger(__name__)

class AmazonScraper(BaseScraper):
    async def extract(self, url: str) -> dict:
        context = await self.create_context()
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await self.delay()

            # Nome do produto
            name_element = await page.query_selector("#productTitle")
            name = await name_element.inner_text() if name_element else "Nome não encontrado"
            name = name.strip()

            # Preço (várias versões da Amazon)
            price = None
            price_selectors = [
                ".a-price .a-offscreen",
                "#priceblock_dealprice",
                "#priceblock_ourprice",
                "span.a-price span.a-offscreen"
            ]
            for sel in price_selectors:
                price_el = await page.query_selector(sel)
                if price_el:
                    price_text = await price_el.get_attribute("innerText") or await price_el.text_content()
                    if price_text:
                        # Remove caracteres não numéricos exceto ponto/vírgula
                        price_text = re.sub(r'[^\d.,]', '', price_text).replace(',', '.')
                        try:
                            price = float(price_text)
                        except:
                            pass
                        break

            # Disponibilidade
            availability = True
            out_of_stock_selectors = [
                "#availability span.a-color-price",
                "#outOfStock",
                "span.a-color-price:has-text('Indisponível')"
            ]
            for sel in out_of_stock_selectors:
                if await page.query_selector(sel):
                    availability = False
                    break

            return {
                "name": name,
                "price": price,
                "availability": availability,
                "currency": "BRL"
            }
        except Exception as e:
            logger.error(f"Erro ao raspar {url}: {e}")
            return None
        finally:
            await context.close()