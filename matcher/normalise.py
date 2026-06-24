import re
_SW = {"woolworths","coles","aldi","homebrand","home","brand","select","macro","odd","bunch","tray","pack","pk","fresh","product","of","the","a","an","and","&"}
_UR = re.compile(r"(\d+(?:\.\d+)?)\s*(kg|g|l|ml|litre|liter|litres|liters|mg|units?|pcs?|pieces?|slices?|sheets?|tabs?|tablets?|caps?|capsules?|sachets?)", re.IGNORECASE)
def normalise(name):
    t = name.lower()
    t = _UR.sub(lambda m: m.group(1)+m.group(2).lower(), t)
    t = re.sub(r"[^\w\s]"," ",t)
    return " ".join(x for x in t.split() if x not in _SW).strip()
