"""Junta todas as fotos de cada anúncio, lendo a página do anúncio. Só busca os que ainda não têm fotos."""
import re
from concurrent.futures import ThreadPoolExecutor

import atualizar as base

MAX_FOTOS = 24


def _numero(i):
    m = re.search(r"(\d+)$", i["id"])
    return m.group(1) if m else ""


def _extrai(i, h):
    h = h.replace("\\u002F", "/").replace("\\/", "/")
    f, pid = i["fonte"], _numero(i)
    if f in ("ABC Imóvel", "SP Imóvel", "ZL Imóvel"):
        pad = r'https://d31hw7dq38n1ek\.cloudfront\.net/Imagens/[^"\' )\\]*/Imovel/%s/G_[^"\' )\\]+?\.(?:webp|jpe?g)' % pid
    elif f == "Chaves na Mão":
        pad = r'https://www\.chavesnamao\.com\.br/imn/1200x0800/N/70/imoveis/\d+/%s/[^"\' )\\]+?\.jpe?g' % pid
    elif f == "Loft":
        lid = i["id"].split("-", 1)[1]
        pad = r'https://content\.loft\.com\.br/homes/%s/desktop_(?:banner|facade\d+)\.jpe?g' % lid
    else:
        return []
    return list(dict.fromkeys(re.findall(pad, h)))[:MAX_FOTOS]


def _busca(i):
    try:
        _, h = base.baixar(i["url"])
        return _extrai(i, h)
    except Exception:
        return []


def preencher(itens, antigas):
    """antigas: {id: [fotos]} da execução anterior. Devolve {id: [fotos]} só dos anúncios atuais."""
    fotos = {i["id"]: antigas[i["id"]] for i in itens if antigas.get(i["id"])}
    falta = [i for i in itens if i["id"] not in fotos]
    with ThreadPoolExecutor(8) as ex:
        for i, achadas in zip(falta, ex.map(_busca, falta)):
            fotos[i["id"]] = achadas or ([i["imagem"]] if i.get("imagem") else [])
    print("fotos: buscadas", len(falta), "de", len(itens))
    return fotos
