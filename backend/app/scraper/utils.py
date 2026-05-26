import random
import asyncio
from typing import List

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
]

def get_random_user_agent() -> str:
    return random.choice(USER_AGENTS)

async def random_delay(min_sec: float = 1.0, max_sec: float = 3.0):
    await asyncio.sleep(random.uniform(min_sec, max_sec))

# Lista vazia de proxies – em produção você carregaria de uma API
PROXIES = []  # ex: ["http://user:pass@proxy1:8000", ...]

def get_random_proxy() -> str | None:
    return random.choice(PROXIES) if PROXIES else None