import re
from bs4 import BeautifulSoup
from .base import BaseScraper

BASE_URL = "https://www.aldi.com.au"
CATEGORIES = [
    {"id": "/en/fresh-food/", "name": "Fresh Food"},
    {"id": "/en/bakery/", "name": "Bakery"},
    {"id": "/en/pantry/", "name": "Pantry"},
    {"id": "/en/dairy-eggs-fridge/", "name": "Dairy, Eggs & Fridge"},
    {"id": "/en/drinks/", "name": "Drinks"},
    {"id": "/en/frozen-food/", "name": "Frozen Food"},
    {"id": "/en/health-beauty/", "name": "Health & Beauty"},
    {"id": "/en/baby/", "name": "Baby"},
    {"id": "/en/household/", "name": "Household"},
    {"id": "/en/pet/", "name": "Pet"},
]

class AldiScraper(BaseScraper):
    STORE_NAME = "ALDI"
    def __init__(self):
        super().__init__(delay=1.5)
        self.session.headers.update({"Accept": "text/html,*/*;q=0.8", "Referer": "https://www.aldi.com.au/"})
    def get_categories(self): return CATEGORIES
    def get_products(self, cat):
        products, page = [], 1
        while True:
            soup = BeautifulSoup(self.get(f"{BASE_URL}{cat['id']}", params={"p": page} if page > 1 else {}).text, "lxml")
            items = soup.select("li.product-item")
            if not items: break
            for item in items:
                p = self._parse(item, cat["name"])
                if p: products.append(p)
            if not soup.select_one("a.next"): break
            page += 1
        return products
    def _parse(self, item, category):
        name_el = item.select_one(".product-name") or item.select_one("h2") or item.select_one(".title")
        if not name_el: return None
        name = name_el.get_text(strip=True)
        link = item.select_one("a[href]")
        url = f"{BASE_URL}{link['href']}" if link else None
        sku = url.rstrip("/").split("/")[-1] if url else name
        price_el = item.select_one(".product-price__saleprice") or item.select_one(".price")
        price = _price(price_el.get_text(strip=True) if price_el else "")
        if price is None: return None
        was_el = item.select_one(".product-price__was") or item.select_one(".old-price")
        was = _price(was_el.get_text(strip=True) if was_el else "")
        on_sale = was is not None and was > price
        img = item.select_one("img")
        img_url = img.get("src") or img.get("data-src") if img else None
        unit_el = item.select_one(".product-price__unit") or item.select_one(".unit-price")
        up, ul = _unit(unit_el.get_text(strip=True) if unit_el else "")
        return {"store": "ALDI", "store_sku": str(sku), "barcode": None, "name": name, "category": category, "image_url": img_url, "current_price": price, "unit_price": up, "unit_label": ul, "is_on_sale": on_sale, "sale_price": price if on_sale else None, "original_price": was if on_sale else None, "url": url}

def _price(t):
    m = re.search(r"\d+\.\d{2}", t.replace(",","")); return float(m.group()) if m else None
def _unit(t):
    if not t: return None, None
    m = re.search(r"\$?([\d.]+)\s*/\s*(.+)", t)
    if m:
        try: return float(m.group(1)), m.group(2).strip()
        except: pass
    return None, None
