"""Distâncias em linha reta: da Cofap (Mauá) e da estação de metrô ou trem mais próxima.
Coordenadas vêm do OpenStreetMap (Nominatim para o bairro, Overpass para as estações) e ficam em cache no repositório."""
import json, math, time, urllib.parse, urllib.request

CACHE, ESTACOES = "coordenadas.json", "estacoes.json"
UA = "casa-nova-abc/1.0 (https://github.com/Raiugami/casa-nova)"
CAIXA = (-23.95, -46.90, -23.35, -46.30)  # sul, oeste, norte, leste: SP e ABC
COFAP_ENDERECO = "Avenida Manoel da Nóbrega 196, Capuava, Mauá, SP, Brasil"
COFAP_FALLBACK = (-23.6695, -46.4395)


def _json(url, dados=None, tentativas=3):
    for t in range(tentativas):
        try:
            req = urllib.request.Request(url, data=dados, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read())
        except Exception as e:
            print("geo:", str(e)[:80])
            time.sleep(5 * (t + 1))
    return None


def _carrega(arq, padrao):
    try:
        return json.load(open(arq, encoding="utf-8"))
    except (OSError, ValueError):
        return padrao


def dentro(lat, lon):
    return CAIXA[0] <= lat <= CAIXA[2] and CAIXA[1] <= lon <= CAIXA[3]


def km(a, b):
    (la1, lo1), (la2, lo2) = a, b
    p = math.pi / 180
    h = math.sin((la2 - la1) * p / 2) ** 2 + math.cos(la1 * p) * math.cos(la2 * p) * math.sin((lo2 - lo1) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


def geocodifica(consulta):
    d = _json("https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=br&q=" + urllib.parse.quote(consulta))
    time.sleep(1.1)  # limite de 1 consulta por segundo do Nominatim
    if d:
        lat, lon = float(d[0]["lat"]), float(d[0]["lon"])
        if dentro(lat, lon):
            return [round(lat, 5), round(lon, 5)]
    return None


def estacoes():
    est = _carrega(ESTACOES, [])
    if est:
        return est
    q = ('[out:json][timeout:60];(node["railway"="station"]["station"~"subway|monorail"](%s,%s,%s,%s);'
         'node["railway"="station"]["network"~"CPTM|Trens Metropolitanos|Metr"](%s,%s,%s,%s););out;') % (CAIXA * 2)
    d = _json("https://overpass-api.de/api/interpreter", ("data=" + urllib.parse.quote(q)).encode())
    vistos = {}
    for e in (d or {}).get("elements", []):
        nome = e.get("tags", {}).get("name")
        if nome and dentro(e["lat"], e["lon"]):
            t = e["tags"]
            tipo = "Metrô" if t.get("station") in ("subway", "monorail") or "Metr" in (t.get("network") or "") and "CPTM" not in (t.get("network") or "") else "Trem"
            vistos.setdefault(nome, [nome, round(e["lat"], 5), round(e["lon"], 5), tipo])
    est = list(vistos.values())
    if len(est) > 30:
        json.dump(est, open(ESTACOES, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("estações:", len(est))
    return est


def preencher(itens):
    """Acrescenta dist_cofap (km), estacao, dist_estacao (km) e tipo_estacao a cada anúncio com coordenada do bairro."""
    cache = _carrega(CACHE, {})
    if "_cofap" not in cache:
        cache["_cofap"] = geocodifica(COFAP_ENDERECO) or list(COFAP_FALLBACK)
    cofap = tuple(cache["_cofap"])
    est = estacoes()
    novos = 0
    for i in itens:
        chave = f"{i['bairro']}|{i['cidade']}"
        if chave not in cache:
            cache[chave] = geocodifica(f"{i['bairro']}, {i['cidade']}, SP, Brasil")
            novos += 1
            if novos % 20 == 0:
                json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        c = cache[chave]
        if not c:
            continue
        i["dist_cofap"] = round(km(c, cofap), 1)
        if est:
            e = min(est, key=lambda x: km(c, (x[1], x[2])))
            i["estacao"], i["dist_estacao"], i["tipo_estacao"] = e[0], round(km(c, (e[1], e[2])), 1), e[3]
    json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("geo: consultas novas", novos, "| com distância", sum(1 for i in itens if "dist_cofap" in i), "de", len(itens))
