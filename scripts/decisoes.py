"""Aplica em decisoes.json as linhas 'aprovar:', 'recusar:' e 'desfazer:' do texto do pedido (variável CORPO)."""
import json, os, re

ARQ = "decisoes.json"
d = json.load(open(ARQ, encoding="utf-8"))
aprov, recus = set(d.get("aprovadas", [])), set(d.get("recusadas", []))
for linha in os.environ.get("CORPO", "").splitlines():
    m = re.match(r"\s*(aprovar|recusar|desfazer):\s*(.*)", linha, re.I)
    if not m:
        continue
    ids = [i.strip() for i in m.group(2).split(",") if re.fullmatch(r"[a-z0-9-]{3,40}", i.strip())]
    for i in ids:
        aprov.discard(i)
        recus.discard(i)
        if m.group(1).lower() == "aprovar":
            aprov.add(i)
        elif m.group(1).lower() == "recusar":
            recus.add(i)
json.dump({"aprovadas": sorted(aprov), "recusadas": sorted(recus)}, open(ARQ, "w", encoding="utf-8"), indent=2)
print("aprovadas:", len(aprov), "recusadas:", len(recus))
