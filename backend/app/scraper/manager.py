from .amazon import AmazonScraper
from typing import Dict

SCRAPER_MAP = {
    "amazon": AmazonScraper,
    # adicione outras lojas aqui
}

async def run_scraper(store: str, url: str) -> Dict:
    scraper_class = SCRAPER_MAP.get(store.lower())
    if not scraper_class:
        raise ValueError(f"Scraper para {store} não implementado")
    scraper = scraper_class()
    return await scraper.extract(url)