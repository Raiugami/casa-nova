"""Mostra os campos de um anúncio da busca da QuintoAndar (teste)."""
import json, sys
sys.path.insert(0, "scripts")
import atualizar as base, fontes_extra as fx
for u in ("https://www.quintoandar.com.br/comprar/imovel/santo-andre-sp-brasil/casa/q-ate-300000",
          "https://www.quintoandar.com.br/comprar/imovel/sao-paulo-sp-brasil/casa/q-ate-300000"):
    d = fx.next_data(u)
    print(u, "next_data:", bool(d))
    if not d:
        continue
    casas = d["props"]["pageProps"]["initialState"]["houses"]
    for h in list(casas.values())[:2]:
        print(json.dumps(h, ensure_ascii=False)[:1500])
    break
