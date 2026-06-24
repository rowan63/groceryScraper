from .client import get_conn

def save_groups(groups):
    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            for g in groups:
                pid = _product(cur, g)
                for sp in g["store_products"]: _store_product(cur, sp, pid)

def _product(cur, g):
    cur.execute('INSERT INTO "Product" ("canonicalName","category","imageUrl","updatedAt") VALUES (%(name)s,%(category)s,%(image_url)s,NOW()) ON CONFLICT DO NOTHING RETURNING id', {"name":g["canonical_name"],"category":g.get("category"),"image_url":g.get("image_url")})
    row = cur.fetchone()
    if row: return row[0]
    cur.execute('SELECT id FROM "Product" WHERE "canonicalName"=%s LIMIT 1', (g["canonical_name"],))
    return cur.fetchone()[0]

def _store_product(cur, sp, pid):
    cur.execute('INSERT INTO "StoreProduct" ("productId",store,"storeSku",barcode,name,"imageUrl",category,"currentPrice","unitPrice","unitLabel","isOnSale","salePrice","originalPrice",url,"updatedAt") VALUES (%(product_id)s,%(store)s,%(store_sku)s,%(barcode)s,%(name)s,%(image_url)s,%(category)s,%(current_price)s,%(unit_price)s,%(unit_label)s,%(is_on_sale)s,%(sale_price)s,%(original_price)s,%(url)s,NOW()) ON CONFLICT (store,"storeSku") DO UPDATE SET "productId"=EXCLUDED."productId",barcode=EXCLUDED.barcode,name=EXCLUDED.name,"imageUrl"=EXCLUDED."imageUrl",category=EXCLUDED.category,"currentPrice"=EXCLUDED."currentPrice","unitPrice"=EXCLUDED."unitPrice","unitLabel"=EXCLUDED."unitLabel","isOnSale"=EXCLUDED."isOnSale","salePrice"=EXCLUDED."salePrice","originalPrice"=EXCLUDED."originalPrice",url=EXCLUDED.url,"updatedAt"=NOW() RETURNING id,"currentPrice","isOnSale","salePrice"', {**sp,"product_id":pid})
    row = cur.fetchone()
    if not row: return
    cur.execute('SELECT price,"isOnSale","salePrice" FROM "PriceHistory" WHERE "storeProductId"=%s ORDER BY "recordedAt" DESC LIMIT 1', (row[0],))
    last = cur.fetchone()
    if last is None or last[0]!=row[1] or last[1]!=row[2] or last[2]!=row[3]:
        cur.execute('INSERT INTO "PriceHistory" ("storeProductId",price,"isOnSale","salePrice","recordedAt") VALUES (%s,%s,%s,%s,NOW())', (row[0],row[1],row[2],row[3]))
