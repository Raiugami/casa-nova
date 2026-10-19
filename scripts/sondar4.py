"""Descobre filtros de preço da Loft, fotos da Loft e URLs por bairro do QuintoAndar."""
import json, re, urllib.request, urllib.error
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
H = {"User-Agent": UA, "Accept-Language": "pt-BR"}
def get(u, h=None):
    return urllib.request.urlopen(urllib.request.Request(u, headers=h or H), timeout=30).read(3_000_000).decode("utf-8", "ignore")
def nd(u):
    return json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', get(u), re.S).group(1))
def loft(u):
    d = nd(u)["props"]["pageProps"]["dehydratedState"]["queries"][0]["state"]["data"]
    precos = [x["listing"]["price"] for x in d["listings"]]
    return d["pagination"]["totalListings"], min(precos), max(precos), len(d["listings"])
base = "https://loft.com.br/venda/casas/sp/santo-andre"
for q in ["", "?precoMaximo=360000", "?preco_max=360000", "?maxPrice=360000", "?priceMax=360000", "?valorMaximo=360000", "?precoMax=360000", "?price_max=360000", "?ordenar=menor-preco", "?ordenacao=menor-preco", "?sort=price_asc", "?quartos=2"]:
    try: print("LOFT", q, loft(base + q))
    except Exception as e: print("LOFT", q, "erro", str(e)[:60])
for u in ["https://loft.com.br/venda/casas/sp/santo-andre/preco-ate-360000", "https://loft.com.br/venda/casas/sp/santo-andre/ate-360000", "https://loft.com.br/venda/casas/sp/santo-andre/vila-palmares_santo-andre_sp", "https://loft.com.br/venda/casas/sp/santo-andre/2-quartos"]:
    try: print("LOFT path", u[-45:], loft(u))
    except Exception as e: print("LOFT path", u[-45:], "erro", str(e)[:60])
fb = nd(base)["props"]["pageProps"]["filterBuilder"]
print("LOFT filterBuilder", json.dumps(fb, ensure_ascii=False)[:1500])
for ref in ["https://loft.com.br/", None]:
    for u in ["https://content.loft.com.br/homes/gfh3fo/banner.jpg", "https://content.loft.com.br/homes/gfh3fo/facade01.jpg", "https://content.loft.com.br/homes/gfh3fo/facade01.jpg?w=400"]:
        h = dict(H); 
        if ref: h["Referer"] = ref
        try: r = urllib.request.urlopen(urllib.request.Request(u, headers=h), timeout=20); print("IMG", ref, r.status, u[-30:])
        except urllib.error.HTTPError as e: print("IMG", ref, e.code, u[-30:])
html = get(base)
print("LOFT img refs", sorted(set(re.findall(r'https://[a-z0-9.-]*loft[a-z0-9.-]*/[^"\' ]{0,100}\.(?:jpg|webp|png)', html)))[:6])
print("LOFT card links", sorted(set(re.findall(r'href="(/imovel/[^"]+)"', html)))[:3])
qa = "https://www.quintoandar.com.br/comprar/imovel/"
for p in ["vila-palmares-santo-andre-sp-brasil/casa", "santo-andre-sp-brasil/casa/q-ate-300000", "santo-andre-sp-brasil/casa/q-ate-360000", "santo-andre-sp-brasil/casa/2-quartos", "santo-andre-sp-brasil/casa/q-de-200000-ate-300000", "santo-andre-sp-brasil/casa/de-2-quartos"]:
    try:
        d = nd(qa + p)["props"]["pageProps"]["initialState"]
        hs = list(d["houses"].values()); pr = [h["salePrice"] for h in hs if h.get("salePrice")]
        print("QA", p, d["search"]["visibleHouses"]["total"], len(hs), (min(pr), max(pr)) if pr else None, sorted({h["regionName"] for h in hs})[:4])
    except Exception as e: print("QA", p, "erro", str(e)[:70])
