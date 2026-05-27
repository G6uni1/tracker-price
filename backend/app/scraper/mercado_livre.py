import re
import logging
from .base import BaseScraper
from playwright.async_api import Page

logger = logging.getLogger(__name__)

class MercadoLivreScraper(BaseScraper):
    async def extract(self, url: str) -> dict | None:
        context = await self.create_context()
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await self.delay()

            # Aceitar cookies se aparecer
            try:
                cookie_btn = page.locator("button:has-text('Entendi')")
                if await cookie_btn.is_visible():
                    await cookie_btn.click()
                    await self.delay()
            except:
                pass

            # Nome do produto
            name = "Nome não encontrado"
            try:
                title = page.locator("h1.ui-pdp-title")
                name = await title.inner_text()
                name = name.strip()
            except:
                pass

            # Preço: tenta vários seletores
            price = None
            price_selectors = [
                ".andes-money-amount__fraction",
                ".ui-pdp-price__second-line .andes-money-amount__fraction",
                "meta[itemprop='price']",
                ".ui-pdp-price__main .andes-money-amount__fraction"
            ]
            for sel in price_selectors:
                try:
                    if sel.startswith("meta"):
                        meta_el = await page.query_selector(sel)
                        if meta_el:
                            content = await meta_el.get_attribute("content")
                            if content:
                                price = float(content)
                                break
                    else:
                        el = page.locator(sel).first
                        text = await el.inner_text()
                        # Remove pontos de milhares e troca vírgula por ponto
                        text = re.sub(r'[^\d,]', '', text).replace('.', '').replace(',', '.')
                        price = float(text)
                        break
                except:
                    continue

            # Disponibilidade
            available = True
            out_stock_indicators = [
                "Estoque esgotado",
                "Produto indisponível",
                "Sem estoque"
            ]
            page_text = await page.inner_text("body")
            if any(ind.lower() in page_text.lower() for ind in out_stock_indicators):
                available = False

            return {
                "name": name,
                "price": price,
                "availability": available,
                "currency": "BRL"
            }
        except Exception as e:
            logger.error(f"Erro Mercado Livre: {e}")
            return None
        finally:
            await context.close()