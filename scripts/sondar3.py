"""Detalhes de campos e URLs de QuintoAndar e Loft."""
import json, re, urllib.request, urllib.error
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
H = {"User-Agent": UA, "Accept-Language": "pt-BR"}
def pagina(u):
    h = urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=30).read(3_000_000).decode("utf-8", "ignore")
    return json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', h, re.S).group(1))
def head(u):
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=H, method="GET"), timeout=20)
        return r.status, r.headers.get("content-type")
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:
        return str(e)[:50], None
def achar(o, pad, p="", out=None):
    out = [] if out is None else out
    if isinstance(o, dict):
        for k, v in o.items():
            if re.search(pad, k, re.I) and not isinstance(v, (dict, list)): out.append((p + "/" + k, v))
            achar(v, pad, p + "/" + k, out)
    elif isinstance(o, list):
        for i, v in enumerate(o[:2]): achar(v, pad, p + f"[{i}]", out)
    return out

q = pagina("https://www.quintoandar.com.br/comprar/imovel/santo-andre-sp-brasil/casa/q-ate-400000")
st = q["props"]["pageProps"]["initialState"]
it = next(iter(st["houses"].values()))
print("QA keys", {k: v for k, v in it.items() if k not in ("photos",)})
print("QA loc", json.dumps(st["search"]["location"], ensure_ascii=False)[:600])
print("QA seo", json.dumps(st["search"]["seo"], ensure_ascii=False)[:500])
print("QA visibleHouses", json.dumps(st["search"]["visibleHouses"], ensure_ascii=False)[:300])
print("QA total?", achar(st["search"], r"total|count|pages|hits")[:10])
for u in ["https://www.quintoandar.com.br/img/med/" + it["banner"], "https://www.quintoandar.com.br/img/xl/" + it["banner"], "https://www.quintoandar.com.br/img/800x600/" + it["banner"], "https://www.quintoandar.com.br/imovel/" + it["id"] + "/comprar"]:
    print("QA head", head(u), u[:110])
for u in ["https://www.quintoandar.com.br/comprar/imovel/santo-andre-sp-brasil/casa/q-ate-400000?pagina=2", "https://www.quintoandar.com.br/comprar/imovel/santo-andre-sp-brasil/casa/q-ate-400000/pagina-2"]:
    try:
        q2 = pagina(u); ids = list(q2["props"]["pageProps"]["initialState"]["houses"])[:3]; print("QA pag", u[-30:], ids)
    except Exception as e: print("QA pag erro", u[-30:], e)

l = pagina("https://loft.com.br/venda/casas/sp/santo-andre")
d = l["props"]["pageProps"]["dehydratedState"]["queries"][0]["state"]["data"]
item = d["listings"][0]["listing"]
print("LOFT item keys", sorted(item.keys()))
print("LOFT item top", [k for k in d["listings"][0].keys()])
print("LOFT url-ish", achar(d["listings"][0], r"slug|url|link|path")[:8])
print("LOFT pagination", json.dumps(d["pagination"]), "search", json.dumps(d["search"], ensure_ascii=False)[:300])
print("LOFT photos/image", item.get("photos"), item.get("image"), item.get("id"))
print("LOFT type fields", {k: item.get(k) for k in ("homeType", "houseType", "realState", "productType", "propertyType", "usageType")}, "addr", item.get("address", {}).get("neighborhood"))
iid = item["id"]
for u in [f"https://content.loft.com.br/homes/{iid}/{item['image']}", f"https://content.loft.com.br/homes/{iid}/{item['photos'][0]}", f"https://loft.com.br/_next/image?url=https%3A%2F%2Fcontent.loft.com.br%2Fhomes%2F{iid}%2F{item['image']}&w=640&q=75"]:
    print("LOFT head", head(u), u[:120])
for u in [f"https://loft.com.br/imovel/{iid}", f"https://loft.com.br/imovel/casa-santo-andre/{iid}?tipoTransacao=venda"]:
    print("LOFT page", head(u), u)
for u in ["https://loft.com.br/venda/casas/sp/santo-andre?pagina=2", "https://loft.com.br/venda/casas/sp/santo-andre?page=2"]:
    try:
        l2 = pagina(u); d2 = l2["props"]["pageProps"]["dehydratedState"]["queries"][0]["state"]["data"]; print("LOFT pag", u[-12:], [x["listing"]["id"] for x in d2["listings"][:3]])
    except Exception as e: print("LOFT pag erro", u[-12:], e)
