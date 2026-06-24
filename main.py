import sys, traceback
from scrapers.woolworths import WoolworthsScraper
from scrapers.coles import ColesScraper
from scrapers.aldi import AldiScraper
from matcher.match import build_canonical_groups
from db.upsert import save_groups
from db.client import close

SCRAPERS = {"woolworths": WoolworthsScraper, "coles": ColesScraper, "aldi": AldiScraper}

def main(stores):
    all_products = []
    for store_name in stores:
        cls = SCRAPERS.get(store_name)
        if not cls:
            print(f"Unknown store: {store_name}")
            continue
        try:
            products = cls().scrape_all()
            print(f"[{store_name.upper()}] Total: {len(products)}")
            all_products.extend(products)
        except Exception:
            print(f"[{store_name.upper()}] Failed:"); traceback.print_exc()
    if not all_products:
        print("No products scraped."); return
    groups = build_canonical_groups(all_products)
    print(f"Matched into {len(groups)} canonical products.")
    save_groups(groups)
    print("Done.")

if __name__ == "__main__":
    args = sys.argv[1:]
    selected = [a.lower() for a in args] if args else list(SCRAPERS.keys())
    try: main(selected)
    finally: close()
