"""Mostra os campos de um anúncio da busca da QuintoAndar (teste)."""
import json, sys
sys.path.insert(0, "scripts")
import fontes_extra as fx
d = fx.next_data("https://www.quintoandar.com.br/comprar/imovel/maua-sp-brasil/casa/q-ate-400000")
casas = d["props"]["pageProps"]["initialState"]["houses"]
for h in list(casas.values())[:2]:
    print(json.dumps(h, ensure_ascii=False)[:1500])
