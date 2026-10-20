"""Junta todas as fotos de cada anúncio, lendo a página do anúncio. Só busca os que ainda não têm fotos."""
import re
import urllib.error
import urllib.request
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
    fotos = {i["id"]: i.pop("fotos") for i in itens if i.get("fotos")}  # já vieram da busca
    fotos.update({i["id"]: antigas[i["id"]] for i in itens if i["id"] not in fotos and antigas.get(i["id"])})
    for i in itens:
        i.pop("fotos", None)
    falta = [i for i in itens if i["id"] not in fotos]
    with ThreadPoolExecutor(8) as ex:
        for i, achadas in zip(falta, ex.map(_busca, falta)):
            fotos[i["id"]] = achadas or ([i["imagem"]] if i.get("imagem") else [])
    print("fotos: buscadas", len(falta), "de", len(itens))
    return fotos


def _no_ar(url):
    """False só quando a foto principal não existe mais (404/410): o anúncio saiu do ar."""
    for metodo in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=metodo, headers={"User-Agent": base.UA})
            with urllib.request.urlopen(req, timeout=20):
                return True
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                return False
        except Exception:
            pass
    return True


def so_com_foto_no_ar(itens, fotos):
    """Tira anúncios sem foto ou cuja foto principal sumiu (QuintoAndar mantém links de anúncios já vendidos)."""
    with ThreadPoolExecutor(16) as ex:
        vivos = list(ex.map(lambda i: bool(fotos.get(i["id"])) and _no_ar(fotos[i["id"]][0]), itens))
    ficam = [i for i, v in zip(itens, vivos) if v]
    for i in itens:
        if i not in ficam:
            fotos.pop(i["id"], None)
    print("fora do ar ou sem foto:", len(itens) - len(ficam))
    return ficam
