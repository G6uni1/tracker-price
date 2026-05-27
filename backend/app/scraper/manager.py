from typing import Dict
from .amazon import AmazonScraper
from .mercado_livre import MercadoLivreScraper
from .latam import LatamScraper  # certifique-se que esse arquivo existe

# Mapeamento de scrapers por loja
SCRAPER_MAP: Dict[str, type] = {
    "amazon": AmazonScraper,
    "mercadolivre": MercadoLivreScraper,
    "latam": LatamScraper,
    # adicione outras lojas aqui
}

async def run_scraper(store: str, url: str) -> dict | None:
    scraper_class = SCRAPER_MAP.get(store.lower())
    if not scraper_class:
        raise ValueError(f"Scraper para {store} não implementado")
    scraper = scraper_class()
    return await scraper.extract_with_retry(url)
