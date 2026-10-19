"""Mostra a estrutura das páginas de listagem de cada fonte (para escrever a leitura de cada uma)."""
import json, re, sys, urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
URLS = {
 "quintoandar": "https://www.quintoandar.com.br/comprar/imovel/santo-andre-sp-brasil/casa",
 "loft": "https://loft.com.br/venda/casas/sp/santo-andre",
 "lopes": "https://www.lopes.com.br/busca/venda/br/sp/santo-andre/tipo/casa-terrea",
 "dreamcasa": "https://www.dreamcasa.com.br/casas-a-venda-em-santo-andre-sp",
 "jordao": "https://www.imoveisjordao.com.br/imoveis/a-venda/casa/maua",
 "belleville": "https://www.bellvilleimoveis.com.br/casa/a-venda/maua-sp/2-quartos",
 "pinotti": "https://www.pinotti.com.br/imoveis/a-venda/sao-bernardo-do-campo",
 "trevisan": "https://www.trevisanabcimoveis.com.br/imoveis/a-venda/casa/sao-bernardo-do-campo/planalto",
}
quais = sys.argv[1:] or list(URLS)
for nome in quais:
    u = URLS[nome]
    print("=" * 30, nome, u)
    try:
        req = urllib.request.Request(u, headers={"User-Agent": UA, "Accept-Language": "pt-BR"})
        h = urllib.request.urlopen(req, timeout=30).read(2_500_000).decode("utf-8", "ignore")
    except Exception as e:
        print("ERRO", e); continue
    nd = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', h, re.S)
    if nd:
        try:
            j = json.loads(nd.group(1))
            def walk(o, p="", d=0):
                if d > 7: return
                if isinstance(o, dict):
                    for k, v in o.items():
                        if isinstance(v, (dict, list)) and len(json.dumps(v)) > 3000:
                            print("  NEXT", p + "/" + k, type(v).__name__, len(v))
                        walk(v, p + "/" + k, d + 1)
                elif isinstance(o, list) and o and d < 7:
                    walk(o[0], p + "[0]", d + 1)
            walk(j)
        except Exception as e:
            print("  next_data erro", e)
    for i, b in enumerate(re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', h, re.S)[:40]):
        tipo = re.search(r'"@type"\s*:\s*"?(\[?[A-Za-z", ]+)', b)
        print("  LD", i, len(b), tipo.group(1) if tipo else "?", re.sub(r"\s+", " ", b)[:260])
    links = re.findall(r'href="([^"]*(?:imovel|casa|venda)[^"]*\d{4,}[^"]*)"', h)
    print("  LINKS", len(set(links)), sorted(set(links))[:6])
    print("  PRECOS", re.findall(r'R\$\s?[\d\.]{5,9}', h)[:8])
