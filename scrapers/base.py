import time, requests
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    STORE_NAME = None
    def __init__(self, delay=1.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36", "Accept-Language": "en-AU,en;q=0.9"})
    def get(self, url, **kw):
        time.sleep(self.delay)
        r = self.session.get(url, timeout=30, **kw); r.raise_for_status(); return r
    @abstractmethod
    def get_categories(self): pass
    @abstractmethod
    def get_products(self, cat): pass
    def scrape_all(self):
        products = []
        for cat in self.get_categories():
            print(f"[{self.STORE_NAME}] {cat['name']}")
            try:
                batch = self.get_products(cat); products.extend(batch); print(f"  -> {len(batch)}")
            except Exception as e: print(f"  x {e}")
        return products
