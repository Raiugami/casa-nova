"""Mede, por fonte, quantos anúncios e fotos estão fora do ar (teste)."""
import json, random, sys, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "scripts")
import atualizar as base
d = json.load(open("imoveis.json")); fotos = json.load(open("fotos.json"))
random.seed(1)
por = {}
for i in d["imoveis"]:
    por.setdefault(i["fonte"], []).append(i)
def foto(u):
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0", "Referer": ""}), timeout=20)
        return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return type(e).__name__
def anuncio(i):
    try:
        final, h = base.baixar(i["url"])
        return final, len(h), h[:0]
    except Exception as e:
        return "ERRO " + str(e)[:60], 0, ""
for fonte, itens in por.items():
    amostra = random.sample(itens, min(12, len(itens)))
    print("==", fonte, len(itens), "itens; sem foto:", sum(1 for i in itens if not fotos.get(i["id"])))
    for i in amostra:
        fs = fotos.get(i["id"], [])
        st = foto(fs[0]) if fs else "sem-foto"
        final, n, _ = anuncio(i)
        print(i["id"], "foto:", st, "| pagina:", "OK" if final == i["url"] or "indisponivel" not in final else "FORA", final[:90], n)
