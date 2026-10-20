"""Testa se sites de imobiliárias respondem e se mostram casas com preço (teste)."""
import re, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "scripts")
import atualizar as base
SITES = {
 "Netimoveis": "https://www.netimoveis.com/venda/sao-paulo/sao-paulo/casa",
 "Lopes": "https://www.lopes.com.br/busca/venda/br/sp/sao-paulo/casa",
 "RE/MAX": "https://www.remax.com.br/imoveis-a-venda/casa/sao-paulo",
 "Century21": "https://www.century21.com.br/imoveis/comprar/casa/sao-paulo",
 "Coelho da Fonseca": "https://www.coelhodafonseca.com.br/venda/imoveis/sao-paulo/casa",
 "Jordao": "https://www.imoveisjordao.com.br/",
 "Belleville": "https://www.bellevilleimoveis.com.br/",
 "Pantera": "https://www.panteraimoveis.com.br/",
 "Jac": "https://www.jacimoveis.com.br/",
 "Pinotti": "https://www.pinotti.com.br/",
 "Tandeli": "https://www.tandeli.com.br/",
 "Moura": "https://www.mouraimoveis.com.br/",
 "Marengo": "https://www.marengoimoveis.com.br/",
 "Graciutti": "https://www.graciutti.com.br/",
 "MGF": "https://www.mgfimoveis.com.br/",
 "Trevisan": "https://www.trevisanimoveis.com.br/",
 "Vitoria": "https://www.vitoriaimoveis.com.br/",
 "Dreamcasa": "https://www.dreamcasa.com.br/",
 "ImovelBrasil": "https://www.imovelbrasil.com.br/",
 "Nuroa": "https://www.nuroa.com.br/venda/casa-sao-paulo",
 "Mitula": "https://casas.mitula.com.br/casas/sao-paulo",
 "Trovit": "https://casas.trovit.com.br/casas-sao-paulo",
 "Nestoria": "https://www.nestoria.com.br/sao-paulo/casa/comprar",
 "MercadoLivre": "https://imoveis.mercadolivre.com.br/casas/venda/sao-paulo/",
 "Wimoveis": "https://www.wimoveis.com.br/casas-venda-sao-paulo-sp.html",
 "QuintoAndar-ok": "https://www.quintoandar.com.br/comprar/imovel/maua-sp-brasil/casa",
 "Apolar": "https://www.apolar.com.br/venda/casa/sao-paulo",
 "Sotheby": "https://www.sothebysrealty.com.br/",
 "DFimoveis": "https://www.dfimoveis.com.br/",
 "Imovelweb": "https://www.imovelweb.com.br/casas-venda-sao-paulo-sp.html",
 "Chaves": "https://www.chavesnamao.com.br/casas-a-venda/sp-maua/",
 "Kenlo": "https://www.imobiliariasantoandre.com.br/",
}
def testa(item):
    nome, url = item
    import urllib.request, urllib.error
    try:
        req = urllib.request.Request(url, headers={"User-Agent": base.UA, "Accept-Language": "pt-BR"})
        with urllib.request.urlopen(req, timeout=25) as r:
            h = r.read(600_000).decode("utf-8", "ignore")
            return nome, r.status, r.geturl()[:70], len(h), len(re.findall(r"R\$\s?[\d.]{5,}", h)), len(re.findall(r"__NEXT_DATA__|application/ld\+json", h))
    except urllib.error.HTTPError as e:
        return nome, e.code, url[:70], 0, 0, 0
    except Exception as e:
        return nome, type(e).__name__, url[:70], 0, 0, 0
with ThreadPoolExecutor(8) as ex:
    for r in ex.map(testa, SITES.items()):
        print("%-18s status=%s bytes=%s precos=%s json=%s -> %s" % (r[0], r[1], r[3], r[4], r[5], r[2]))
