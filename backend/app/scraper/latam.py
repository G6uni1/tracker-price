import re
import logging
from .base import BaseScraper
from playwright.async_api import Page

logger = logging.getLogger(__name__)

class LatamScraper(BaseScraper):
    async def extract(self, url: str) -> dict | None:
        context = await self.create_context()
        page = await context.new_page()
        try:
            # Aumenta timeout pois sites de voo podem ser lentos
            await page.goto(url, wait_until="networkidle", timeout=90000)
            await self.delay(min_sec=3, max_sec=6)  # maior delay para carregar voos

            # Nome da rota (origem-destino) – podemos usar o título da página
            title = await page.title()
            name = title.strip() if title else "Voo"

            # Preço – geralmente em uma classe específica ou com aria-label
            price = None
            # Tenta pegar o menor preço visível
            price_elements = page.locator("[class*='price'], [class*='amount'], .fare-amount")
            if await price_elements.count() > 0:
                # Itera e pega o menor valor numérico
                texts = await price_elements.all_inner_texts()
                numeric_prices = []
                for t in texts:
                    nums = re.findall(r'[\d.,]+', t)
                    for n in nums:
                        try:
                            clean = n.replace('.', '').replace(',', '.')
                            val = float(clean)
                            if val > 10:  # ignora valores irreais
                                numeric_prices.append(val)
                        except:
                            pass
                if numeric_prices:
                    price = min(numeric_prices)

            # Caso não encontre, tenta via meta
            if not price:
                meta_price = await page.query_selector("meta[itemprop='price']")
                if meta_price:
                    content = await meta_price.get_attribute("content")
                    if content:
                        price = float(content)

            # Disponibilidade: se encontrou preço, está disponível
            available = price is not None

            return {
                "name": name,
                "price": price,
                "availability": available,
                "currency": "BRL"
            }
        except Exception as e:
            logger.error(f"Erro Latam: {e}")
            return None
        finally:
            await context.close()