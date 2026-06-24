from .base import BaseScraper

class ColesScraper(BaseScraper):
    STORE_NAME = "COLES"
    def __init__(self):
        super().__init__(delay=1.2)
        self.session.headers.update({"Accept": "application/json, text/plain, */*", "Referer": "https://www.coles.com.au/browse", "oai-country-version": "AU"})

    def get_categories(self):
        data = self.get("https://www.coles.com.au/api/2.0.0/page/categorytree").json()
        return [{"id": c.get("seoToken") or c.get("uniqueID"), "name": c["name"]} for c in data.get("catalogGroupView", []) if c.get("name")]

    def get_products(self, cat):
        products, page = [], 1
        while True:
            data = self.get("https://www.coles.com.au/api/2.0.0/page/category/products", params={"slug": cat["id"], "page": page}).json()
            res = data.get("productResults", {}); items = res.get("results", [])
            if not items: break
            for item in items:
                p = self._parse(item, cat["name"])
                if p: products.append(p)
            if page * res.get("pageSize", 48) >= res.get("noOfResults", 0): break
            page += 1
        return products

    def _parse(self, item, category):
        sku = item.get("id"); name = item.get("name", "").strip()
        if not sku or not name: return None
        pr = item.get("pricing", {}); price = pr.get("now")
        if price is None: return None
        was = pr.get("was"); on_sale = was is not None and float(was) > float(price)
        up, ul = _comparable(pr.get("comparable", ""))
        imgs = item.get("imageUris", []); img = imgs[0].get("uri") if imgs else None
        return {"store": "COLES", "store_sku": str(sku), "barcode": item.get("barcode"), "name": name, "category": category, "image_url": img, "current_price": float(price), "unit_price": up, "unit_label": ul, "is_on_sale": on_sale, "sale_price": float(price) if on_sale else None, "original_price": float(was) if on_sale else None, "url": f"https://www.coles.com.au/product/{item.get('seoToken', sku)}"}

def _comparable(s):
    if not s: return None, None
    try:
        parts = s.replace("$","").replace(" per ","/").split("/"); return float(parts[0].strip()), f"per {parts[1].strip()}" if len(parts)>1 else None
    except: return None, None
