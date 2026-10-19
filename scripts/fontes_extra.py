"""Fontes com dados estruturados: QuintoAndar e Loft. Cada função devolve anúncios no mesmo formato do atualizar.py."""
import json, re
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import atualizar as base

NEXT = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)
PASTAS = {"Santo André": "santo-andre", "Mauá": "maua", "São Bernardo do Campo": "sao-bernardo-do-campo", "São Paulo": "sao-paulo"}


def next_data(url):
    final, h = base.baixar(url)
    m = NEXT.search(h)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except ValueError:
        return None


def bairros(cidade):
    return sorted({base.sem_acento(b).replace(" ", "-") for b in base.BOA[cidade] + base.ATENCAO[cidade]})


def localizacao(cidade, bairro):
    sb = base.sem_acento(bairro)
    if sb in base.ATENCAO.get(cidade, []):
        return "atencao"
    return "boa" if sb in base.BOA.get(cidade, []) else "media"


NOTA = {"boa": "Bairro consolidado e bem servido.", "media": "Bairro residencial; confirme topografia e entorno.", "atencao": "Região periférica ou com ruas em morro."}


def monta(id_, fonte, cidade, bairro, preco, quartos, vagas, area, url, imagem, data, extras=""):
    loc = localizacao(cidade, bairro)
    return {"id": id_, "cidade": cidade, "bairro": bairro, "preco": preco, "quartos": quartos, "vagas": vagas, "area": area,
            "tipo": "Casa (confirmar tipo)", "extras": extras[:140], "fonte": fonte, "url": url, "link_direto": True,
            "anuncio_data": data, "imagem": imagem, "localizacao": loc, "nota_local": NOTA[loc]}


# ------------------------------------------------------------------ QuintoAndar
def quintoandar_pagina(url):
    d = next_data(url)
    try:
        casas = d["props"]["pageProps"]["initialState"]["houses"]
    except (TypeError, KeyError):
        return []
    saida = []
    for h in casas.values():
        if not isinstance(h, dict) or h.get("type") != "Casa" or not h.get("forSale"):
            continue
        preco, q = h.get("salePrice") or 0, h.get("bedrooms") or 0
        cidade = (h.get("address") or {}).get("city")
        if not preco or preco > base.PRECO_MAX or q < 2 or cidade not in base.CIDADES.values():
            continue
        if base.BLOQUEIO.search(h.get("shortSaleDescription") or ""):
            continue
        bairro = h.get("neighbourhood") or h.get("regionName") or ""
        saida.append(monta(f"quinto-{h['id']}", "QuintoAndar", cidade, bairro, preco, q, h.get("parkingSpots"), h.get("area"),
                           f"https://www.quintoandar.com.br/imovel/{h['id']}/comprar",
                           f"https://www.quintoandar.com.br/img/800x600/{h['banner']}" if h.get("banner") else None, None,
                           h.get("shortSaleDescription") or ""))
    return saida


def coletar_quintoandar():
    urls = []
    for cidade, pasta in PASTAS.items():
        loc = f"{pasta}-sp-brasil"
        for teto in ("200000", "300000", "400000"):
            urls.append(f"https://www.quintoandar.com.br/comprar/imovel/{loc}/casa/q-ate-{teto}")
        for b in bairros(cidade):
            for teto in ("300000", "400000"):
                urls.append(f"https://www.quintoandar.com.br/comprar/imovel/{b}-{loc}/casa/q-ate-{teto}")
    with ThreadPoolExecutor(6) as ex:
        return [i for lote in ex.map(quintoandar_pagina, urls) for i in lote]


# ------------------------------------------------------------------ Loft
def loft_pagina(url):
    d = next_data(url)
    try:
        itens = d["props"]["pageProps"]["dehydratedState"]["queries"][0]["state"]["data"]["listings"]
    except (TypeError, KeyError, IndexError):
        return []
    saida = []
    for it in itens:
        l = it.get("listing") or {}
        if l.get("homeType") != "house" or l.get("houseType") != "STANDARD" or l.get("status") != "FOR_SALE":
            continue
        preco, q = l.get("price") or 0, l.get("bedrooms") or 0
        ad = l.get("address") or {}
        cidade = ad.get("city")
        if not preco or preco > base.PRECO_MAX or q < 2 or cidade not in base.CIDADES.values():
            continue
        desc = l.get("description") or ""
        if base.BLOQUEIO.search(desc):
            continue
        data = (l.get("updatedAt") or "")[:10] or None
        if data and (date.today() - date.fromisoformat(data)).days > 365:
            continue
        saida.append(monta(f"loft-{l['id']}", "Loft", cidade, ad.get("neighborhood") or "", preco, q, l.get("parkingSpots"), l.get("area"),
                           f"https://loft.com.br/imovel/{l['id']}?tipoTransacao=venda",
                           f"https://content.loft.com.br/homes/{l['id']}/banner_thumbnail.jpg", data, desc))
    return saida


def loft_busca(base_url):
    achados = []
    for n in range(0, 8):
        lote = loft_pagina(f"{base_url}?pagina={n}" if n else base_url)
        if n and not lote and n > 2:
            break
        achados += lote
    return achados


def coletar_loft():
    urls = []
    for cidade, pasta in PASTAS.items():
        urls.append(f"https://loft.com.br/venda/casas/sp/{pasta}")
        for b in bairros(cidade):
            urls.append(f"https://loft.com.br/venda/casas/sp/{pasta}/{b}_{pasta}_sp")
    with ThreadPoolExecutor(6) as ex:
        return [i for lote in ex.map(loft_busca, urls) for i in lote]


FONTES = {"quintoandar": coletar_quintoandar, "loft": coletar_loft}
