"""Mostra as fotos que cada fonte oferece na página do anúncio (teste)."""
import json, re, sys
sys.path.insert(0, "scripts")
import atualizar as base
IMG = re.compile(r'https?:[^"\'\s<>)\\]+?\.(?:jpe?g|webp|png)', re.I)
d = json.load(open("imoveis.json"))
vistos = {}
for i in d["imoveis"]:
    vistos.setdefault(i["fonte"], i)
for fonte, i in vistos.items():
    try:
        final, h = base.baixar(i["url"])
    except Exception as e:
        print(fonte, "ERRO", e); continue
    imgs = list(dict.fromkeys(IMG.findall(h.replace("\\u002F", "/").replace("\\/", "/"))))
    print("==", fonte, i["url"], "->", final, len(h), "bytes", len(imgs), "imagens")
    for u in imgs[:25]:
        print("  ", u)
