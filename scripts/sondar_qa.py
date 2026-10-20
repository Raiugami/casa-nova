"""Procura sinais de sobrado nos anúncios da QuintoAndar (teste)."""
import json, re, sys
sys.path.insert(0, "scripts")
import fontes_extra as fx
SIN = re.compile(r"escada|andar|superior|sobrado|pavimento|mezanino|térreo|terreo", re.I)
tot = com = 0
for pasta in ("santo-andre", "sao-bernardo-do-campo", "maua", "sao-paulo"):
    d = fx.next_data(f"https://www.quintoandar.com.br/comprar/imovel/{pasta}-sp-brasil/casa/q-ate-300000")
    if not d:
        print(pasta, "sem dados"); continue
    casas = d["props"]["pageProps"]["initialState"]["houses"]
    for h in casas.values():
        if not isinstance(h, dict) or h.get("type") != "Casa":
            continue
        tot += 1
        subs = [f.get("subtitle") or "" for f in h.get("photos") or [] if isinstance(f, dict)]
        achou = [x for x in subs if SIN.search(x)]
        achou2 = SIN.findall(json.dumps({k: v for k, v in h.items() if k != "photos"}, ensure_ascii=False))
        if achou or achou2:
            com += 1
            print(h["id"], achou[:3], achou2[:4])
    if tot and pasta == "santo-andre":
        print("chaves:", sorted(k for k in h.keys()))
print("total", tot, "com sinal", com)
