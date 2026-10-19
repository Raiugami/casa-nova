"""Mostra exemplos de anúncios dentro do JSON de QuintoAndar e Loft."""
import json, re, urllib.request
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
def pagina(u):
    h = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA, "Accept-Language": "pt-BR"}), timeout=30).read(3_000_000).decode("utf-8", "ignore")
    return json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', h, re.S).group(1))

q = pagina("https://www.quintoandar.com.br/comprar/imovel/santo-andre-sp-brasil/casa/q-ate-400000")
hs = q["props"]["pageProps"]["initialState"]["houses"]
print("QA houses keys:", list(hs)[:6], "n=", len(hs))
for k in list(hs)[:2]:
    print("QA item", k, json.dumps(hs[k], ensure_ascii=False)[:1400])
print("QA search keys", list(q["props"]["pageProps"]["initialState"]["search"].keys()))
print("QA search.visibleHouses?", json.dumps({k: (v if not isinstance(v,(list,dict)) else type(v).__name__+str(len(v))) for k,v in q["props"]["pageProps"]["initialState"]["search"].items()}, ensure_ascii=False)[:1500])

l = pagina("https://loft.com.br/venda/casas/sp/santo-andre")
data = l["props"]["pageProps"]["dehydratedState"]["queries"][0]["state"]["data"]
print("LOFT data keys", list(data))
for it in data["listings"][:2]:
    print("LOFT item", json.dumps(it, ensure_ascii=False)[:1500])
print("LOFT other", {k: (v if not isinstance(v,(list,dict)) else type(v).__name__+str(len(v))) for k,v in data.items()})
