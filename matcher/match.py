import os
from thefuzz import fuzz
from .normalise import normalise
THRESHOLD = int(os.getenv("FUZZY_THRESHOLD","88"))

def build_canonical_groups(products):
    bc_idx, groups = {}, []
    for p in products:
        idx = _by_barcode(p, bc_idx)
        if idx is None: idx = _by_name(p, groups)
        if idx is not None:
            groups[idx]["store_products"].append(p); _idx_bc(p, idx, bc_idx)
        else:
            i = len(groups)
            groups.append({"canonical_name": _name(p["name"]), "category": p.get("category"), "image_url": p.get("image_url"), "store_products": [p]})
            _idx_bc(p, i, bc_idx)
    return groups

def _by_barcode(p, bc_idx):
    bc = p.get("barcode"); return bc_idx.get(str(bc)) if bc else None

def _by_name(p, groups):
    norm = normalise(p["name"]); best, best_i = 0, None
    for i, g in enumerate(groups):
        for sp in g["store_products"]:
            if sp["store"] == p["store"]: continue
            s = fuzz.token_sort_ratio(norm, normalise(sp["name"]))
            if s > best: best, best_i = s, i
    return best_i if best >= THRESHOLD else None

def _idx_bc(p, i, bc_idx):
    bc = p.get("barcode")
    if bc: bc_idx[str(bc)] = i

def _name(name):
    for pre in ["Woolworths ","Coles ","ALDI "]:
        if name.startswith(pre): return name[len(pre):]
    return name
