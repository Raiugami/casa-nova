"""Procura onde a QuintoAndar guarda as fotos de um anúncio (teste)."""
import json, re, sys
sys.path.insert(0, "scripts")
import atualizar as base, fontes_extra as fx
d = json.load(open("imoveis.json"))
qa = [i for i in d["imoveis"] if i["fonte"] == "QuintoAndar"][:2]
def varre(o, caminho="", saida=None):
    saida = [] if saida is None else saida
    if isinstance(o, dict):
        for k, v in o.items():
            c = caminho + "." + k
            if re.search(r"photo|image|foto|banner|pictur|galler|media", k, re.I):
                saida.append((c, json.dumps(v)[:300]))
            varre(v, c, saida)
    elif isinstance(o, list):
        for n, v in enumerate(o[:3]):
            varre(v, caminho + "[]", saida)
    return saida
for i in qa:
    print("==", i["url"], i["imagem"])
    nd = fx.next_data(i["url"])
    if not nd:
        print("sem NEXT_DATA"); continue
    for c, v in varre(nd)[:25]:
        print(c, v)
