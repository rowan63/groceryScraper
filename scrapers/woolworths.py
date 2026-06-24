from .base import BaseScraper

class WoolworthsScraper(BaseScraper):
    STORE_NAME = "WOOLWORTHS"
    def __init__(self):
        super().__init__(delay=1.2)
        self.session.headers.update({"Accept": "application/json, text/plain, */*", "Referer": "https://www.woolworths.com.au/shop/browse"})

    def get_categories(self):
        data = self.get("https://www.woolworths.com.au/apis/ui/PiesCategoriesWithSpecials").json()
        return [{"id": c["NodeId"], "name": c["Description"]} for c in data.get("Categories", []) if c.get("NodeId")]

    def get_products(self, cat):
        products, page = [], 1
        while True:
            data = self.get("https://www.woolworths.com.au/apis/ui/browse/category", params={"categoryId": cat["id"], "pageNumber": page, "pageSize": 36, "sortType": "TraderRelevance", "filters": ""}).json()
            bundles = data.get("Bundles", [])
            if not bundles: break
            for b in bundles:
                for item in b.get("Products", []):
                    p = self._parse(item, cat["name"])
                    if p: products.append(p)
            if page >= data.get("TotalRecordCount", 0) // 36 + 1: break
            page += 1
        return products

    def _parse(self, item, category):
        sku = item.get("Stockcode"); name = item.get("Name", "").strip()
        if not sku or not name: return None
        pi = item.get("Price", {}); price = pi.get("Now") or pi.get("Was")
        if price is None: return None
        was = pi.get("Was"); on_sale = was is not None and was > price
        cup = item.get("CupString", ""); up, ul = _cup(cup)
        return {"store": "WOOLWORTHS", "store_sku": str(sku), "barcode": item.get("Barcode"), "name": name, "category": category, "image_url": item.get("LargeImageFile") or item.get("SmallImageFile"), "current_price": float(price), "unit_price": up, "unit_label": ul, "is_on_sale": on_sale, "sale_price": float(price) if on_sale else None, "original_price": float(was) if on_sale else None, "url": f"https://www.woolworths.com.au/shop/productdetails/{sku}"}

def _cup(s):
    if not s: return None, None
    try:
        parts = s.replace("$","").split("/"); return float(parts[0].strip()), parts[1].strip() if len(parts)>1 else None
    except: return None, None
